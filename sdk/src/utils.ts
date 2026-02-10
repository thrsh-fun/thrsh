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

