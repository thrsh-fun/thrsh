use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct GlobalState {
    pub authority: Pubkey,
    pub scan_count: u64,
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
    pub staleness_threshold: u64,
    pub paused: bool,
    pub bump: u8,
}

impl GlobalState {
    pub const SIZE: usize = 8 + 32 + 8 + 8 + 8 + 8 + 1 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct ScanConfig {
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
    pub staleness_threshold: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct MarketInput {
    pub market_key: Pubkey,
    pub platform: Platform,
    pub event_id: [u8; 32],
    pub yes_price: u64,
    pub no_price: u64,
    pub volume: u64,
    pub liquidity: u64,
    pub last_updated: u64,
}

#[account]
pub struct MarketAccount {
    pub platform: Platform,
    pub event_id: [u8; 32],
    pub yes_price: u64,
    pub no_price: u64,
    pub volume: u64,
    pub liquidity: u64,
    pub status: MarketStatus,
    pub last_updated: u64,
    pub bump: u8,
}

impl MarketAccount {
    pub const SIZE: usize = 8 + 1 + 32 + 8 + 8 + 8 + 8 + 1 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct EventMatch {
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub similarity_score: u16,
    pub spread_bps: u64,
    pub timestamp: u64,
}

#[account]
pub struct Position {
    pub owner: Pubkey,
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub side: Side,
    pub amount: u64,
    pub entry_yield: u64,
    pub opened_at: u64,
    pub bump: u8,
}

impl Position {
    pub const SIZE: usize = 8 + 32 + 32 + 32 + 1 + 8 + 8 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct ArbitrageOpportunity {
    pub match_id: [u8; 32],
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub yield_est: u64,
    pub confidence: u16,
    pub kelly_fraction: u64,
    pub timestamp: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum Platform {
    Polymarket,
    Drift,
    Hedgehog,
    MetaDAO,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum MarketStatus {
    Active,
    Settling,
    Settled,
    Expired,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum Side {
    Yes,
    No,
}
