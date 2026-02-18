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

  /**
   * Scan connected prediction markets and return matched event pairs.
   *
   * Fetches all MarketAccount entries from the program, filters by the
   * provided config thresholds, and pairs events across platforms.
   */
  async scanMarkets(config: ScanConfig): Promise<ScanResult> {
    const [globalPDA] = this.getGlobalStatePDA();

    const accounts = await this.retryRpc(() =>
      this.connection.getProgramAccounts(PROGRAM_ID, {
        commitment: this.commitment,
        filters: [{ dataSize: 85 }],
      })
    );

    const markets: MarketAccount[] = accounts.map((acc) =>
      this.deserializeMarket(acc.account.data)
    );

    const filtered = markets.filter(
      (m) =>
        m.liquidity.gte(config.minLiquidity) &&
        new BN(Date.now() / 1000)
          .sub(m.lastUpdated)
          .lte(config.stalenessThreshold)
    );

    const matches: EventMatch[] = [];
    for (let i = 0; i < filtered.length; i++) {
      for (let j = i + 1; j < filtered.length; j++) {
        const a = filtered[i];
        const b = filtered[j];

        if (a.platform === b.platform) continue;

        const similarity = this.computeSimilarity(a.eventId, b.eventId);
        if (similarity < 800) continue;

        const spread = this.computeSpreadBps(a.yesPrice, b.yesPrice);
        if (spread.gt(config.maxSpreadBps)) continue;

        matches.push({
          marketA: accounts[i].pubkey,
          marketB: accounts[j].pubkey,
          similarityScore: similarity,
          spreadBps: spread,
          timestamp: new BN(Math.floor(Date.now() / 1000)),
        });
      }
    }

    return {
      matches,
      scannedAt: Date.now(),
      marketsProcessed: filtered.length,
    };
  }

  /**
   * Analyze a matched event pair and determine if an arbitrage opportunity
   * exists with sufficient yield.
   */
  async detectArbitrage(
    match_: EventMatch,
    minYieldBps: number
  ): Promise<DetectResult | null> {
    const marketAInfo = await this.retryRpc(() =>
      this.connection.getAccountInfo(match_.marketA)
    );
    const marketBInfo = await this.retryRpc(() =>
      this.connection.getAccountInfo(match_.marketB)
    );

    if (!marketAInfo || !marketBInfo) {
      return null;
    }

    const marketA = this.deserializeMarket(marketAInfo.data);
    const marketB = this.deserializeMarket(marketBInfo.data);

    const combined = marketA.yesPrice.add(marketB.yesPrice);
    const scale = new BN(10_000);

    if (combined.gte(scale)) {
      return null;
    }

    const yieldEst = scale.sub(combined);
    if (yieldEst.toNumber() < minYieldBps) {
      return null;
    }

    const kellyFraction = this.kellyFraction(
      marketA.yesPrice,
      marketB.yesPrice,
      scale
    );

    return {
      opportunity: {
        matchId: this.deriveMatchId(match_.marketA, match_.marketB),
        marketA: match_.marketA,
        marketB: match_.marketB,
        yieldEst,
        confidence: match_.similarityScore,
        kellyFraction,
        timestamp: new BN(Math.floor(Date.now() / 1000)),
      },
      detectedAt: Date.now(),
    };
  }

  /**
   * Execute a harvest transaction for a detected arbitrage opportunity.
   * Builds and sends the transaction atomically.
   */
  async executeHarvest(
    opportunity: ArbitrageOpportunity,
    amount: BN,
    vaultAddress: PublicKey
  ): Promise<HarvestResult> {
    const [globalPDA] = this.getGlobalStatePDA();
    const [positionPDA] = this.getPositionPDA(this.wallet.publicKey);

    const ix = new TransactionInstruction({
      keys: [
        { pubkey: globalPDA, isSigner: false, isWritable: false },
        { pubkey: positionPDA, isSigner: false, isWritable: true },
        { pubkey: vaultAddress, isSigner: false, isWritable: true },
        { pubkey: this.wallet.publicKey, isSigner: true, isWritable: true },
      ],
      programId: PROGRAM_ID,
      data: Buffer.from([]),
    });

    const tx = new Transaction().add(ix);
    const sig = await this.provider.sendAndConfirm(tx);

    return {
