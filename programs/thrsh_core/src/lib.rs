use anchor_lang::prelude::*;

pub mod contexts;
pub mod errors;
pub mod events;
pub mod state;

use contexts::*;
use errors::ThrshError;
use events::*;
use state::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod thrsh_core {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, config: ScanConfig) -> Result<()> {
        let global = &mut ctx.accounts.global_state;
        global.authority = ctx.accounts.authority.key();
        global.scan_count = 0;
        global.min_liquidity = config.min_liquidity;
        global.max_spread_bps = config.max_spread_bps;
        global.staleness_threshold = config.staleness_threshold;
        global.paused = false;
        global.bump = ctx.bumps.global_state;

        emit!(Initialized {
            authority: global.authority,
            min_liquidity: global.min_liquidity,
            max_spread_bps: global.max_spread_bps,
        });

        Ok(())
    }

    pub fn scan_markets(
        ctx: Context<ScanMarkets>,
        markets: Vec<MarketInput>,
    ) -> Result<Vec<EventMatch>> {
        let global = &mut ctx.accounts.global_state;
        require!(!global.paused, ThrshError::ProtocolPaused);

        let clock = Clock::get()?;
        let now = clock.unix_timestamp as u64;

        let mut matches: Vec<EventMatch> = Vec::new();
        let filtered: Vec<&MarketInput> = markets
            .iter()
            .filter(|m| m.liquidity >= global.min_liquidity)
            .filter(|m| now.saturating_sub(m.last_updated) <= global.staleness_threshold)
            .collect();

        for i in 0..filtered.len() {
            for j in (i + 1)..filtered.len() {
                let a = filtered[i];
                let b = filtered[j];

                if a.platform == b.platform {
                    continue;
                }

                let similarity = compute_similarity(&a.event_id, &b.event_id);
                if similarity < 800 {
                    continue;
                }

                let spread = compute_spread_bps(a.yes_price, b.yes_price);
                if spread > global.max_spread_bps {
                    continue;
                }

                matches.push(EventMatch {
                    market_a: a.market_key,
                    market_b: b.market_key,
                    similarity_score: similarity,
                    spread_bps: spread,
                    timestamp: now,
                });
            }
        }

        global.scan_count = global.scan_count.checked_add(1).unwrap();

        for m in &matches {
            emit!(MatchFound {
                market_a: m.market_a,
                market_b: m.market_b,
                similarity_score: m.similarity_score,
                spread_bps: m.spread_bps,
            });
        }

        Ok(matches)
    }

    pub fn detect_arbitrage(
        ctx: Context<DetectArbitrage>,
        match_data: EventMatch,
    ) -> Result<ArbitrageOpportunity> {
        let global = &ctx.accounts.global_state;
        require!(!global.paused, ThrshError::ProtocolPaused);

        let market_a = &ctx.accounts.market_a;
        let market_b = &ctx.accounts.market_b;

        let combined = market_a
            .yes_price
            .checked_add(market_b.yes_price)
            .ok_or(ThrshError::MathOverflow)?;

        require!(combined < 10_000, ThrshError::NoArbitrageFound);

        let gap_bps = 10_000u64.saturating_sub(combined);
        require!(gap_bps >= 50, ThrshError::SpreadTooNarrow);

        let yield_est = thrsh_math::expected_value(
            market_a.yes_price,
            market_b.yes_price,
