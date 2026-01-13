use anchor_lang::prelude::*;

#[event]
pub struct Initialized {
    pub authority: Pubkey,
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
}

#[event]
