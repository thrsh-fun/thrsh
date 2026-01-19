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
