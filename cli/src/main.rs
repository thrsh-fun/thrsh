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
        amount: u64,
    },
}

fn main() {
    let cli = Cli::parse();

    let client = RpcClient::new_with_commitment(
        cli.rpc_url.clone(),
        CommitmentConfig::confirmed(),
    );

    let keypair = cli.keypair.as_ref().map(|path| {
        read_keypair_file(path).unwrap_or_else(|err| {
            eprintln!("Failed to read keypair from {}: {}", path.display(), err);
            std::process::exit(1);
        })
    });

    match cli.command {
        Commands::Scan {
            min_liquidity,
            max_staleness,
        } => {
            println!(
                "Scanning markets (min_liquidity={}, max_staleness={}s)",
                min_liquidity, max_staleness
            );
            let version = client.get_version().unwrap_or_else(|err| {
                eprintln!("RPC connection failed: {}", err);
                std::process::exit(1);
            });
            println!("Connected to Solana {}", version.solana_core);

            match cli.format {
                OutputFormat::Table => {
                    println!("{:<44} {:<44} {:<8} {:<10}", "Market A", "Market B", "Score", "Spread");
                    println!("{}", "-".repeat(110));
                }
                OutputFormat::Json => {
                    println!("[]");
                }
            }
        }
        Commands::Detect { min_yield_bps } => {
            println!("Detecting arbitrage (min_yield={}bps)", min_yield_bps);
            let _kp = keypair.as_ref().unwrap_or_else(|| {
                eprintln!("Keypair required for detect command");
                std::process::exit(1);
            });
        }
        Commands::Harvest { match_id, amount } => {
            println!("Executing harvest (match={}, amount={})", match_id, amount);
            let _kp = keypair.as_ref().unwrap_or_else(|| {
                eprintln!("Keypair required for harvest command");
                std::process::exit(1);
            });
        }
    }
}
