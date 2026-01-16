use anchor_lang::prelude::*;

#[event]
pub struct Initialized {
    pub authority: Pubkey,
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
}

#[event]
pub struct MatchFound {
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub similarity_score: u16,
    pub spread_bps: u64,
}

#[event]
pub struct ArbitrageDetected {
    pub match_id: [u8; 32],
