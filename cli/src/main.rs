use clap::{Parser, Subcommand};
use solana_client::rpc_client::RpcClient;
use solana_sdk::commitment_config::CommitmentConfig;
use solana_sdk::signature::read_keypair_file;
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "thrsh")]
#[command(about = "Cross-market prediction market arbitrage scanner")]
#[command(version)]
struct Cli {
    /// Solana RPC URL
    #[arg(long, default_value = "https://api.mainnet-beta.solana.com")]
    rpc_url: String,

    /// Path to keypair file
    #[arg(long, env = "THRSH_KEYPAIR")]
    keypair: Option<PathBuf>,

    /// Output format
    #[arg(long, default_value = "table")]
    format: OutputFormat,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Clone, Debug, clap::ValueEnum)]
enum OutputFormat {
    Table,
    Json,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan prediction markets for matching events
    Scan {
        /// Minimum liquidity threshold in lamports
        #[arg(long, default_value = "1000000000")]
        min_liquidity: u64,

        /// Maximum staleness in seconds
        #[arg(long, default_value = "60")]
        max_staleness: u64,
    },
    /// Detect arbitrage opportunities from matched events
    Detect {
        /// Minimum yield in basis points
        #[arg(long, default_value = "50")]
        min_yield_bps: u64,
    },
    /// Execute a harvest on a detected opportunity
    Harvest {
        /// Match ID (hex encoded)
        #[arg(long)]
        match_id: String,

        /// Amount in lamports
        #[arg(long)]
