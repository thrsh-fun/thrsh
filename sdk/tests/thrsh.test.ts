import { PublicKey } from "@solana/web3.js";
import BN from "bn.js";
import {
  priceToBps,
  bpsToPrice,
  isArbitrage,
  expectedYield,
  spreadBps,
  formatBps,
  lamportsToSol,
} from "../src/utils";

describe("thrsh SDK utilities", () => {
  describe("priceToBps", () => {
    it("converts 0.45 to 4500 bps", () => {
      const result = priceToBps(0.45);
      expect(result.toNumber()).toBe(4500);
    });

    it("converts 1.0 to 10000 bps", () => {
      const result = priceToBps(1.0);
      expect(result.toNumber()).toBe(10000);
    });

    it("throws for negative prices", () => {
      expect(() => priceToBps(-0.1)).toThrow();
    });

    it("throws for prices above 1.0", () => {
      expect(() => priceToBps(1.5)).toThrow();
    });
  });

  describe("bpsToPrice", () => {
    it("converts 4500 bps to 0.45", () => {
      expect(bpsToPrice(new BN(4500))).toBeCloseTo(0.45);
    });

    it("converts 10000 bps to 1.0", () => {
      expect(bpsToPrice(new BN(10000))).toBeCloseTo(1.0);
    });
  });

  describe("isArbitrage", () => {
    it("returns true when combined price is below 10000 bps", () => {
      expect(isArbitrage(new BN(4500), new BN(4500))).toBe(true);
    });

