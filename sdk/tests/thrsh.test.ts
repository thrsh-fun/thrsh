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

    it("returns false when combined price equals 10000 bps", () => {
      expect(isArbitrage(new BN(5000), new BN(5000))).toBe(false);
    });

    it("returns false when combined price exceeds 10000 bps", () => {
      expect(isArbitrage(new BN(6000), new BN(5000))).toBe(false);
    });
  });

  describe("expectedYield", () => {
    it("calculates correct yield for a 1000bps gap", () => {
      const y = expectedYield(new BN(4500), new BN(4500));
      expect(y.toNumber()).toBe(1000);
    });

    it("returns zero when no gap exists", () => {
      const y = expectedYield(new BN(5000), new BN(5000));
      expect(y.toNumber()).toBe(0);
    });
  });

  describe("spreadBps", () => {
    it("calculates absolute spread between two prices", () => {
      const s = spreadBps(new BN(4800), new BN(4500));
      expect(s.toNumber()).toBe(300);
    });

    it("returns zero for equal prices", () => {
      const s = spreadBps(new BN(4500), new BN(4500));
      expect(s.toNumber()).toBe(0);
    });
  });

  describe("formatBps", () => {
    it("formats 250 bps as 2.50%", () => {
      expect(formatBps(new BN(250))).toBe("2.50%");
    });
  });

  describe("lamportsToSol", () => {
    it("converts 1 SOL worth of lamports", () => {
      expect(lamportsToSol(new BN(1_000_000_000))).toBe("1.0000");
    });

    it("handles fractional SOL", () => {
      expect(lamportsToSol(new BN(500_000_000), 2)).toBe("0.50");
    });
  });
});
