//! Fixed-point arithmetic utilities for prediction-market arbitrage.
//!
//! All prices and probabilities are expressed in basis points (bps)
//! where 10 000 bps = 100 %.

/// Calculate the Kelly fraction for a two-outcome arbitrage position.
///
/// Given `price_a` and `price_b` in basis points, where buying YES on
/// market A at `price_a` and YES on market B at `price_b` produces a
/// guaranteed profit when `price_a + price_b < scale`, this function
/// returns the optimal fraction of bankroll to wager (in bps).
pub fn kelly_fraction(price_a: u128, price_b: u128, scale: u128) -> u128 {
    if price_a == 0 || price_b == 0 || scale == 0 {
        return 0;
    }

    let combined = price_a.saturating_add(price_b);
    if combined >= scale {
        return 0;
    }

    let edge = scale.saturating_sub(combined);
    let odds = scale
        .checked_mul(scale)
        .unwrap_or(0)
        .checked_div(combined.max(1))
        .unwrap_or(0);

    if odds <= scale {
        return 0;
    }

    let b = odds.saturating_sub(scale);
    let p = edge
        .checked_mul(scale)
        .unwrap_or(0)
        .checked_div(scale.max(1))
        .unwrap_or(0);

    let numerator = b.checked_mul(p).unwrap_or(0);
    let denominator = b.checked_mul(scale).unwrap_or(0);

    if denominator == 0 {
        return 0;
    }

    let fraction = numerator
        .checked_mul(scale)
        .unwrap_or(0)
        .checked_div(denominator)
        .unwrap_or(0);

    fraction.min(scale)
}

/// Compute the expected value in basis points for an arbitrage position.
///
/// Returns the expected profit per unit wagered, scaled to `scale` bps.
pub fn expected_value(price_a: u64, price_b: u64, scale: u64) -> u64 {
    let combined = price_a.saturating_add(price_b);
    if combined >= scale {
        return 0;
    }
    scale.saturating_sub(combined)
}

/// Convert a market price (in bps) to an implied probability (in bps).
pub fn implied_probability(price_bps: u64, scale: u64) -> u64 {
    price_bps.min(scale)
