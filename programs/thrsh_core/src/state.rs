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
