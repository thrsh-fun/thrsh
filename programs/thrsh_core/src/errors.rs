use anchor_lang::prelude::*;

#[error_code]
pub enum ThrshError {
    #[msg("No arbitrage opportunity found for the given market pair")]
    NoArbitrageFound,

    #[msg("Spread is too narrow to justify execution costs")]
    SpreadTooNarrow,

    #[msg("Market price data is stale and must be refreshed")]
    StalePriceData,

