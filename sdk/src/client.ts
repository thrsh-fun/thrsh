import {
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  TransactionInstruction,
  Commitment,
} from "@solana/web3.js";
import { Program, AnchorProvider, Wallet, BN } from "@coral-xyz/anchor";
import {
  MarketAccount,
  EventMatch,
  ArbitrageOpportunity,
  ScanConfig,
  ScanResult,
  DetectResult,
  HarvestResult,
} from "./types";

const PROGRAM_ID = new PublicKey(
  "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"
);

const GLOBAL_SEED = Buffer.from("global");
const POSITION_SEED = Buffer.from("position");

/** Maximum number of RPC retry attempts for transient failures. */
const MAX_RETRIES = 3;

/** Delay between retries in milliseconds. */
const RETRY_DELAY_MS = 1000;

/**
 * ThrshClient provides methods to interact with the thrsh on-chain program.
 *
 * Handles connection management, account fetching, and transaction building
 * for the scan-detect-harvest arbitrage pipeline.
 */
export class ThrshClient {
  private connection: Connection;
  private wallet: Wallet;
  private provider: AnchorProvider;
  private commitment: Commitment;

  constructor(
    rpcUrl: string,
    wallet: Wallet,
    commitment: Commitment = "confirmed"
  ) {
    this.commitment = commitment;
    this.connection = new Connection(rpcUrl, this.commitment);
    this.wallet = wallet;
    this.provider = new AnchorProvider(this.connection, this.wallet, {
      commitment: this.commitment,
    });
  }

  /** Derive the global state PDA. */
  private getGlobalStatePDA(): [PublicKey, number] {
    return PublicKey.findProgramAddressSync([GLOBAL_SEED], PROGRAM_ID);
  }

  /** Derive a position PDA for a given owner. */
  private getPositionPDA(owner: PublicKey): [PublicKey, number] {
    return PublicKey.findProgramAddressSync(
      [POSITION_SEED, owner.toBuffer()],
      PROGRAM_ID
    );
  }

