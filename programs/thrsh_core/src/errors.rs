use anchor_lang::prelude::*;

#[error_code]
pub enum ThrshError {
    #[msg("No arbitrage opportunity found for the given market pair")]
    NoArbitrageFound,

    #[msg("Spread is too narrow to justify execution costs")]
    SpreadTooNarrow,

    #[msg("Market price data is stale and must be refreshed")]
    StalePriceData,

    #[msg("Arithmetic overflow in price calculation")]
    MathOverflow,

    #[msg("Unauthorized access attempt")]
    Unauthorized,

    #[msg("Position size exceeds maximum allowed by Kelly criterion")]
    PositionTooLarge,

    #[msg("Invalid amount: must be greater than zero")]
    InvalidAmount,

    #[msg("Protocol is currently paused by admin")]
