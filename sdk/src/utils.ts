import BN from "bn.js";

const SCALE = new BN(10_000);

/**
 * Convert a decimal price (0.0 - 1.0) to basis points.
 */
export function priceToBps(price: number): BN {
  if (price < 0 || price > 1) {
    throw new Error("Price must be between 0.0 and 1.0");
  }
  return new BN(Math.round(price * 10_000));
}

/**
 * Convert basis points to a decimal price (0.0 - 1.0).
 */
export function bpsToPrice(bps: BN): number {
  return bps.toNumber() / 10_000;
}

/**
 * Calculate the implied probability from a market price in basis points.
 */
export function impliedProbability(priceBps: BN): number {
  return bpsToPrice(priceBps);
}

/**
 * Calculate the spread between two prices in basis points.
 */
export function spreadBps(priceA: BN, priceB: BN): BN {
  const diff = priceA.gt(priceB) ? priceA.sub(priceB) : priceB.sub(priceA);
  return diff;
}

/**
 * Check if two prices represent an arbitrage opportunity.
 * An opportunity exists when YES_A + YES_B < SCALE.
 */
export function isArbitrage(yesPriceA: BN, yesPriceB: BN): boolean {
  return yesPriceA.add(yesPriceB).lt(SCALE);
}

/**
 * Calculate the expected yield from an arbitrage position.
 */
export function expectedYield(yesPriceA: BN, yesPriceB: BN): BN {
  const combined = yesPriceA.add(yesPriceB);
  if (combined.gte(SCALE)) return new BN(0);
  return SCALE.sub(combined);
}

/**
 * Format a BN value as a human-readable basis points string.
 */
export function formatBps(bps: BN): string {
  const value = bps.toNumber();
  return (value / 100).toFixed(2) + "%";
}

/**
 * Format lamports to SOL with specified decimal places.
 */
export function lamportsToSol(lamports: BN, decimals: number = 4): string {
  const sol = lamports.toNumber() / 1_000_000_000;
  return sol.toFixed(decimals);
}

/**
 * Sleep utility for async retry logic.
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
