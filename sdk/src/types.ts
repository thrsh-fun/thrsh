import { PublicKey } from "@solana/web3.js";
import BN from "bn.js";

export enum Platform {
  Polymarket = 0,
  Drift = 1,
  Hedgehog = 2,
  MetaDAO = 3,
}

export enum MarketStatus {
  Active = 0,
  Settling = 1,
  Settled = 2,
  Expired = 3,
}

export enum Side {
  Yes = 0,
  No = 1,
}

export interface MarketAccount {
  platform: Platform;
  eventId: Uint8Array;
  yesPrice: BN;
  noPrice: BN;
  volume: BN;
  liquidity: BN;
  status: MarketStatus;
  lastUpdated: BN;
}

export interface EventMatch {
  marketA: PublicKey;
  marketB: PublicKey;
  similarityScore: number;
  spreadBps: BN;
  timestamp: BN;
}

export interface Position {
