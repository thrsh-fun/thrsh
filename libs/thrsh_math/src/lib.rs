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
}

/// Detect whether a probability gap exists between two markets.
///
/// Returns `true` if `price_a + price_b < scale - threshold_bps`.
pub fn has_probability_gap(price_a: u64, price_b: u64, scale: u64, threshold_bps: u64) -> bool {
    let combined = price_a.saturating_add(price_b);
    combined < scale.saturating_sub(threshold_bps)
}

/// Calculate optimal bet sizing given Kelly fraction and bankroll.
///
/// Returns the amount to wager, clamped to `max_position`.
pub fn optimal_bet_size(kelly_bps: u64, bankroll: u64, max_position: u64) -> u64 {
    let raw = bankroll
        .checked_mul(kelly_bps)
        .unwrap_or(0)
        .checked_div(10_000)
        .unwrap_or(0);
    raw.min(max_position)
}

/// Fractional Kelly: apply a conservative multiplier (in bps) to
/// the full Kelly fraction.
pub fn fractional_kelly(full_kelly_bps: u128, fraction_bps: u128, scale: u128) -> u128 {
    full_kelly_bps
        .checked_mul(fraction_bps)
        .unwrap_or(0)
        .checked_div(scale.max(1))
        .unwrap_or(0)
}

/// Geometric mean return for a series of outcome yields (each in bps).
///
/// Uses the product of (1 + yield/scale) terms, then extracts the nth root
/// approximation via iterative averaging.
pub fn geometric_mean_return(yields: &[u64], scale: u64) -> u64 {
    if yields.is_empty() || scale == 0 {
        return 0;
    }

    let mut product: u128 = scale as u128;
    for &y in yields {
        product = product
            .checked_mul((scale as u128).saturating_add(y as u128))
            .unwrap_or(0)
            .checked_div(scale as u128)
            .unwrap_or(0);
    }

    let n = yields.len() as u32;
    let mut guess = product / (yields.len() as u128).max(1);
    for _ in 0..20 {
        if guess == 0 {
            break;
        }
        let powered = iterative_pow(guess, n, scale as u128);
        let adjustment = product
            .checked_mul(scale as u128)
            .unwrap_or(0)
            .checked_div(powered.max(1))
            .unwrap_or(0);
        guess = (guess.saturating_add(adjustment)) / 2;
    }

    guess.saturating_sub(scale as u128) as u64
}

fn iterative_pow(base: u128, exp: u32, scale: u128) -> u128 {
    let mut result = scale;
    for _ in 0..exp {
        result = result.checked_mul(base).unwrap_or(0).checked_div(scale.max(1)).unwrap_or(0);
    }
    result
}

/// Compute variance of yield samples (in bps squared).
pub fn yield_variance(yields: &[u64], scale: u64) -> u64 {
    if yields.len() < 2 || scale == 0 {
        return 0;
    }
    let n = yields.len() as u64;
    let mean = yields.iter().copied().sum::<u64>() / n;
    let sum_sq: u64 = yields
        .iter()
        .map(|&y| {
            let diff = if y > mean { y - mean } else { mean - y };
            diff.saturating_mul(diff)
        })
        .sum();
    sum_sq / (n - 1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn kelly_zero_when_no_edge() {
        assert_eq!(kelly_fraction(5_000, 5_000, 10_000), 0);
    }

    #[test]
    fn kelly_positive_when_edge_exists() {
        let f = kelly_fraction(4_000, 4_000, 10_000);
        assert!(f > 0, "expected positive kelly fraction, got {}", f);
    }

    #[test]
    fn expected_value_basic() {
        assert_eq!(expected_value(4_500, 4_500, 10_000), 1_000);
        assert_eq!(expected_value(5_000, 5_000, 10_000), 0);
    }

    #[test]
    fn probability_gap_detection() {
        assert!(has_probability_gap(4_000, 4_000, 10_000, 100));
        assert!(!has_probability_gap(5_000, 5_000, 10_000, 100));
    }

    #[test]
    fn optimal_bet_respects_max() {
        let bet = optimal_bet_size(2_000, 100_000, 5_000);
        assert_eq!(bet, 5_000);
    }

    #[test]
    fn fractional_kelly_halves() {
        let full = 2_000u128;
        let half = fractional_kelly(full, 5_000, 10_000);
        assert_eq!(half, 1_000);
    }

    #[test]
    fn variance_of_identical_values_is_zero() {
        assert_eq!(yield_variance(&[100, 100, 100], 10_000), 0);
    }
}
