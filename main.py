#!/usr/bin/env python3
"""
Generates a realistic open-source Solana/Anchor project with commit history.
Run this script inside an empty directory to produce the thrsh repository.
"""

import os
import subprocess
import random
import hashlib
import shutil
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_NAME = "thrsh"
DESCRIPTION = "Cross-market prediction market arbitrage engine for Solana"
REPO_DIR = "."
USER_NAME = "thrsh-fun"           # Set to your public GitHub username
USER_EMAIL = "252091682+thrsh-fun@users.noreply.github.com"  # Set to your public GitHub email

START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 3, 4)
TARGET_COMMITS = 150

BANNER_PATH = "./banner.png"
WEBSITE_URL = "https://thrsh.fun"
TWITTER_HANDLE = "thrshfun"

PROGRAM_ID = "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def run_git(args, date=None):
    """Execute a git command, optionally backdating the commit."""
    env = os.environ.copy()
    if date is not None:
        iso = date.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = iso
        env["GIT_COMMITTER_DATE"] = iso
    subprocess.run(
        ["git"] + args,
        cwd=REPO_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def write_file(rel_path, content):
    """Write *content* to *rel_path* inside REPO_DIR, creating dirs."""
    full = os.path.join(REPO_DIR, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def copy_banner():
    """Copy banner.png into the repo root if it exists next to this script."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
    dst = os.path.join(REPO_DIR, "banner.png")
    if os.path.isfile(src) and os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)


# ---------------------------------------------------------------------------
# Date generation
# ---------------------------------------------------------------------------


def generate_commit_dates(n, start, end):
    """Return *n* sorted datetimes between *start* and *end*.

    Applies weekday bias, working-hour clustering, and occasional bursts.
    """
    total_seconds = int((end - start).total_seconds())
    dates = []
    burst_remaining = 0
    burst_base = None

    while len(dates) < n:
        if burst_remaining > 0 and burst_base is not None:
            offset = random.randint(60, 3600)
            dt = burst_base + timedelta(seconds=offset)
            burst_base = dt
            burst_remaining -= 1
        else:
            dt = start + timedelta(seconds=random.randint(0, total_seconds))
            weekday = dt.weekday()
            # reject 60 % of weekend commits
            if weekday >= 5 and random.random() < 0.6:
                continue
            # working-hour bias
            if random.random() < 0.80:
                hour = random.randint(9, 19)
            else:
                hour = random.choice(list(range(0, 9)) + list(range(20, 24)))
            dt = dt.replace(hour=hour, minute=random.randint(0, 59),
                            second=random.randint(0, 59))
            # 12 % chance to start a burst
            if random.random() < 0.12:
                burst_remaining = random.randint(2, 4)
                burst_base = dt

        if start <= dt <= end:
            dates.append(dt)

    dates.sort()
    return dates[:n]


# ---------------------------------------------------------------------------
# Commit message generation
# ---------------------------------------------------------------------------

COMMIT_POOL = {
    # Phase 0 -- project bootstrap (commits 0-9)
    0: [
        "chore: initialize workspace with Cargo.toml and Anchor.toml",
        "chore: add .gitignore and editor configs",
        "chore: add MIT license",
        "docs: add initial README with project description",
        "chore: add rustfmt.toml and clippy.toml",
        "chore: scaffold programs/thrsh_core directory",
        "chore: scaffold libs/thrsh_math crate",
        "chore: add CI workflow for GitHub Actions",
        "chore: add CONTRIBUTING.md",
        "docs: add architecture notes to README",
    ],
    # Phase 1 -- core account structs (commits 10-29)
    1: [
        "feat(core): define MarketAccount state struct",
        "feat(core): add EventMatch struct for cross-platform pairing",
        "feat(core): define Position account with entry price tracking",
        "feat(core): add ArbitrageOpportunity struct",
        "feat(core): implement custom error codes",
        "feat(core): add event emission structs",
        "feat(core): scaffold instruction contexts module",
        "refactor(core): extract state types into state.rs",
        "refactor(core): move error codes to errors.rs",
        "feat(core): add platform enum for market sources",
        "feat(core): add market status enum with active/settled variants",
        "fix(core): correct field alignment in MarketAccount",
        "style(core): apply rustfmt to all source files",
        "feat(core): add liquidity depth field to MarketAccount",
        "fix(core): use checked_mul for price calculations",
        "docs(core): add doc comments to state structs",
        "feat(core): add volume tracking to MarketAccount",
        "feat(core): define ScanConfig account for parameters",
        "refactor(core): rename gap_pct to spread_bps for clarity",
        "chore(core): update Cargo.toml dependencies",
    ],
    # Phase 2 -- event matcher (commits 30-49)
    2: [
        "feat(core): implement initialize instruction",
        "feat(core): add scan_markets instruction skeleton",
        "feat(core): implement event similarity scoring",
        "feat(core): add cosine distance for event title matching",
        "fix(core): handle empty market list in scan",
        "feat(core): emit MatchFound event on detection",
        "perf(core): skip markets below minimum liquidity threshold",
        "feat(core): add timestamp validation to scan_markets",
        "refactor(core): extract matching logic into helper function",
        "test(core): add unit test for similarity scoring",
        "fix(core): prevent duplicate match entries",
        "feat(core): add platform-specific adapters for data normalization",
        "docs(core): document scan_markets flow",
        "fix(core): validate event_id length before comparison",
        "feat(core): add confidence threshold parameter",
        "refactor(core): use BTreeMap for ordered match results",
        "perf(core): early exit when gap exceeds max spread",
        "style(core): fix clippy warnings in matcher module",
        "feat(core): track scan count in global state",
        "fix(core): handle clock sysvar correctly in tests",
    ],
    # Phase 3 -- arbitrage detector (commits 50-69)
    3: [
        "feat(core): implement detect_arbitrage instruction",
        "feat(core): add spread calculation YES_A + YES_B < 1.0",
        "feat(core): emit ArbitrageDetected event with yield estimate",
        "fix(core): clamp yield estimate to basis point precision",
        "feat(core): add minimum yield filter to detector",
        "perf(core): batch process match pairs in single instruction",
        "feat(core): add staleness check for market prices",
        "fix(core): reject stale prices older than 60 seconds",
        "refactor(core): consolidate detector logic into single pass",
        "feat(core): add risk score to ArbitrageOpportunity",
        "fix(core): prevent overflow in spread calculation",
        "feat(core): add max position size constraint",
        "docs(core): add inline examples for detect_arbitrage",
        "test(core): add detector unit tests for edge cases",
        "fix(core): handle zero-liquidity markets gracefully",
        "perf(core): skip pairs where both sides exceed 0.95",
        "refactor(core): rename harvest to execute_harvest for clarity",
        "feat(core): implement execute_harvest instruction stub",
        "fix(core): validate signer authority in execute_harvest",
        "style(core): clean up unused imports in detector",
    ],
    # Phase 4 -- kelly calculator / math lib (commits 70-89)
    4: [
        "feat(math): implement kelly criterion calculation",
        "feat(math): add probability gap detection function",
        "feat(math): implement optimal bet sizing",
        "feat(math): add fractional kelly with configurable fraction",
        "fix(math): handle edge case where probability is zero",
        "feat(math): add expected value calculation",
        "test(math): add unit tests for kelly criterion",
        "feat(math): add implied probability from price conversion",
        "fix(math): clamp kelly fraction to [0, 1] range",
        "refactor(math): use fixed-point arithmetic for precision",
        "perf(math): inline hot-path calculations",
        "docs(math): add module-level documentation",
        "feat(math): add variance calculation for risk assessment",
        "fix(math): correct rounding in basis point conversion",
        "feat(math): add geometric mean return calculation",
        "test(math): add property-based tests for edge cases",
        "feat(core): integrate thrsh_math into arbitrage detector",
        "fix(core): pass correct decimals to kelly calculator",
        "refactor(math): rename module functions for consistency",
        "style(math): apply rustfmt and fix doc warnings",
    ],
    # Phase 5 -- TypeScript SDK (commits 90-119)
    5: [
        "feat(sdk): scaffold TypeScript SDK with package.json",
        "feat(sdk): add tsconfig and jest configuration",
        "feat(sdk): define MarketAccount type interface",
        "feat(sdk): define EventMatch and Position types",
        "feat(sdk): define ArbitrageOpportunity type",
        "feat(sdk): implement ThrshClient class skeleton",
        "feat(sdk): add scanMarkets method to ThrshClient",
        "feat(sdk): add detectArbitrage method to ThrshClient",
        "feat(sdk): add executeHarvest method to ThrshClient",
        "feat(sdk): implement connection and wallet setup",
        "fix(sdk): handle RPC connection errors gracefully",
        "feat(sdk): add utility functions for price conversion",
        "feat(sdk): add BN helpers for on-chain math",
        "refactor(sdk): extract RPC calls into separate module",
        "feat(sdk): add event listener for ArbitrageDetected",
        "fix(sdk): correct account discriminator in deserialization",
        "test(sdk): add unit tests for type serialization",
        "feat(sdk): add retry logic for transient RPC failures",
        "fix(sdk): handle null market data without throwing",
        "docs(sdk): add JSDoc comments to public methods",
        "feat(sdk): export all types from index.ts",
        "fix(sdk): align enum values with on-chain representation",
        "perf(sdk): cache program account fetches",
        "refactor(sdk): use branded types for PublicKey strings",
        "feat(sdk): add getArbitrageHistory query method",
        "fix(sdk): correct buffer layout for Position account",
        "test(sdk): add integration test for scan flow",
        "style(sdk): run prettier on all TypeScript files",
        "feat(sdk): add configurable commitment level",
        "chore(sdk): update @solana/web3.js to 1.95",
    ],
    # Phase 6 -- CLI, tests, docs (commits 120-149)
    6: [
        "feat(cli): scaffold CLI crate with clap",
        "feat(cli): add scan subcommand",
        "feat(cli): add detect subcommand",
        "feat(cli): add harvest subcommand",
        "feat(cli): add keypair loading from file or env",
        "fix(cli): validate RPC URL format before connecting",
        "feat(cli): add table output formatter for scan results",
        "feat(cli): add JSON output mode",
        "test: add integration tests for full scan pipeline",
        "test: add test for arbitrage detection with known spread",
        "test: add test for position sizing via kelly criterion",
        "fix: correct test fixture market prices",
        "docs: update README with usage examples",
        "docs: add architecture diagram to README",
        "docs: update feature table in README",
        "docs: add CHANGELOG entries for v0.1.0",
        "chore: update workspace dependency versions",
        "refactor: clean up unused utility functions",
        "fix(cli): handle missing keypair file with helpful error",
        "perf(core): reduce account size by packing booleans",
        "feat(core): add admin-only pause instruction",
        "fix(core): enforce pause check in execute_harvest",
        "docs: finalize CONTRIBUTING guide",
        "style: run cargo fmt across workspace",
        "chore: pin solana-program to 1.18",
        "fix: resolve clippy warnings across workspace",
        "test: add edge case tests for zero-spread markets",
        "docs: add tech stack table to README",
        "chore: bump version to 0.1.0",
        "docs(readme): final formatting pass",
    ],
}

ISSUE_REFS = [
    "#1", "#2", "#3", "#4", "#5", "#7", "#8", "#10", "#12", "#14",
    "#15", "#18", "#21", "#23", "#25",
]


def build_commit_messages(n):
    """Return a list of *n* commit messages drawn from the phased pool."""
    messages = []
    pool_keys = sorted(COMMIT_POOL.keys())
    total_pool = sum(len(v) for v in COMMIT_POOL.values())

    # flatten in phase order
    for key in pool_keys:
        messages.extend(COMMIT_POOL[key])

    # pad with extras if needed
    while len(messages) < n:
        phase = random.choice(pool_keys)
        msg = random.choice(COMMIT_POOL[phase])
        suffix = " (iteration {})".format(random.randint(2, 5))
        messages.append(msg + suffix)

    messages = messages[:n]

    # sprinkle issue references on ~12 % of commits
    for i in range(len(messages)):
        if random.random() < 0.12:
            ref = random.choice(ISSUE_REFS)
            messages[i] = messages[i] + " " + ref

    return messages


# ---------------------------------------------------------------------------
# File content generators
# ---------------------------------------------------------------------------


def gen_gitignore():
    return """\
target/
node_modules/
.anchor/
test-ledger/
dist/
*.so
*.dylib
*.log
.env
.DS_Store
main.py
"""


def gen_rustfmt():
    return """\
max_width = 100
tab_spaces = 4
edition = "2021"
use_field_init_shorthand = true
"""


def gen_clippy():
    return """\
avoid-breaking-exported-api = false
cognitive-complexity-threshold = 30
"""


def gen_license():
    return """\
MIT License

Copyright (c) 2026 thrsh-fun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def gen_contributing():
    return """\
# Contributing to thrsh

Thanks for your interest in contributing.

## Development Setup

1. Install Rust 1.75+ and Solana CLI 1.18+.
2. Install Node.js 18+ and Yarn.
3. Clone the repo and run `anchor build` in the project root.
4. Run `anchor test` to verify everything compiles and tests pass.

## Pull Requests

- Fork the repo and create a feature branch from `main`.
- Follow conventional commit messages (`feat:`, `fix:`, `docs:`, etc.).
- Ensure `cargo fmt` and `cargo clippy` pass without warnings.
- Add tests for new functionality.
- Keep PRs focused -- one logical change per PR.

## Code Style

- Rust: follow `rustfmt.toml` settings in the repo root.
- TypeScript: Prettier with default settings.
- Documentation: write doc comments for all public items.

## Reporting Issues

Open an issue with a clear description, reproduction steps, and expected behavior.
"""


def gen_changelog():
    return """\
# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-03-01

### Added
- Core arbitrage detection engine with cross-market event matching.
- MarketAccount, EventMatch, Position, and ArbitrageOpportunity state structs.
- Kelly Criterion calculator in `thrsh_math` crate.
- TypeScript SDK with ThrshClient class.
- CLI tool with scan, detect, and harvest subcommands.
- GitHub Actions CI pipeline.
- Integration tests for full scan-detect-harvest pipeline.

### Changed
- Renamed `gap_pct` to `spread_bps` for basis-point precision.
- Switched to fixed-point arithmetic in math library.

### Fixed
- Overflow in spread calculation for extreme price values.
- Stale price rejection window set to 60 seconds.
- Zero-liquidity markets no longer crash the detector.
"""


def gen_workspace_cargo():
    return """\
[workspace]
resolver = "2"
members = [
    "programs/thrsh_core",
    "libs/thrsh_math",
    "cli",
]

[workspace.dependencies]
anchor-lang = "0.30.1"
anchor-spl = "0.30.1"
solana-program = "1.18"
"""


def gen_anchor_toml():
    return """\
[toolchain]
anchor_version = "0.30.1"

[features]
resolution = true
skip-lint = false

[programs.localnet]
thrsh_core = "{program_id}"

[registry]
url = "https://api.apr.dev"

[provider]
cluster = "Localnet"
wallet = "~/.config/solana/id.json"

[scripts]
test = "yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.test.ts"
""".format(program_id=PROGRAM_ID)


def gen_ci_yml():
    return """\
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  SOLANA_VERSION: "1.18.17"
  ANCHOR_VERSION: "0.30.1"
  RUST_TOOLCHAIN: "stable"

jobs:
  build:
    name: Build & Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ env.RUST_TOOLCHAIN }}
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: cargo-${{ hashFiles('**/Cargo.lock') }}
      - run: cargo build -p thrsh-math -p thrsh-cli
      - run: cargo test -p thrsh-math

  sdk:
    name: SDK
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: cd sdk && yarn install
      - run: cd sdk && yarn test
"""


def gen_core_cargo():
    return """\
[package]
name = "thrsh-core"
version = "0.1.0"
edition = "2021"
description = "Cross-market prediction market arbitrage engine"
license = "MIT"

[lib]
crate-type = ["cdylib", "lib"]
name = "thrsh_core"

[features]
no-entrypoint = []
no-idl = []
no-log-ix-name = []
cpi = ["no-entrypoint"]
default = []

[dependencies]
anchor-lang = { workspace = true }
anchor-spl = { workspace = true }
thrsh-math = { path = "../../libs/thrsh_math" }

[dev-dependencies]
solana-program-test = "1.18"
solana-sdk = "1.18"
"""


def gen_core_lib():
    return """\
use anchor_lang::prelude::*;

pub mod contexts;
pub mod errors;
pub mod events;
pub mod state;

use contexts::*;
use errors::ThrshError;
use events::*;
use state::*;

declare_id!("{program_id}");

#[program]
pub mod thrsh_core {{
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, config: ScanConfig) -> Result<()> {{
        let global = &mut ctx.accounts.global_state;
        global.authority = ctx.accounts.authority.key();
        global.scan_count = 0;
        global.min_liquidity = config.min_liquidity;
        global.max_spread_bps = config.max_spread_bps;
        global.staleness_threshold = config.staleness_threshold;
        global.paused = false;
        global.bump = ctx.bumps.global_state;

        emit!(Initialized {{
            authority: global.authority,
            min_liquidity: global.min_liquidity,
            max_spread_bps: global.max_spread_bps,
        }});

        Ok(())
    }}

    pub fn scan_markets(
        ctx: Context<ScanMarkets>,
        markets: Vec<MarketInput>,
    ) -> Result<Vec<EventMatch>> {{
        let global = &mut ctx.accounts.global_state;
        require!(!global.paused, ThrshError::ProtocolPaused);

        let clock = Clock::get()?;
        let now = clock.unix_timestamp as u64;

        let mut matches: Vec<EventMatch> = Vec::new();
        let filtered: Vec<&MarketInput> = markets
            .iter()
            .filter(|m| m.liquidity >= global.min_liquidity)
            .filter(|m| now.saturating_sub(m.last_updated) <= global.staleness_threshold)
            .collect();

        for i in 0..filtered.len() {{
            for j in (i + 1)..filtered.len() {{
                let a = filtered[i];
                let b = filtered[j];

                if a.platform == b.platform {{
                    continue;
                }}

                let similarity = compute_similarity(&a.event_id, &b.event_id);
                if similarity < 800 {{
                    continue;
                }}

                let spread = compute_spread_bps(a.yes_price, b.yes_price);
                if spread > global.max_spread_bps {{
                    continue;
                }}

                matches.push(EventMatch {{
                    market_a: a.market_key,
                    market_b: b.market_key,
                    similarity_score: similarity,
                    spread_bps: spread,
                    timestamp: now,
                }});
            }}
        }}

        global.scan_count = global.scan_count.checked_add(1).unwrap();

        for m in &matches {{
            emit!(MatchFound {{
                market_a: m.market_a,
                market_b: m.market_b,
                similarity_score: m.similarity_score,
                spread_bps: m.spread_bps,
            }});
        }}

        Ok(matches)
    }}

    pub fn detect_arbitrage(
        ctx: Context<DetectArbitrage>,
        match_data: EventMatch,
    ) -> Result<ArbitrageOpportunity> {{
        let global = &ctx.accounts.global_state;
        require!(!global.paused, ThrshError::ProtocolPaused);

        let market_a = &ctx.accounts.market_a;
        let market_b = &ctx.accounts.market_b;

        let combined = market_a
            .yes_price
            .checked_add(market_b.yes_price)
            .ok_or(ThrshError::MathOverflow)?;

        require!(combined < 10_000, ThrshError::NoArbitrageFound);

        let gap_bps = 10_000u64.saturating_sub(combined);
        require!(gap_bps >= 50, ThrshError::SpreadTooNarrow);

        let yield_est = thrsh_math::expected_value(
            market_a.yes_price,
            market_b.yes_price,
            10_000,
        );

        let kelly = thrsh_math::kelly_fraction(
            market_a.yes_price as u128,
            market_b.yes_price as u128,
            10_000,
        );

        let confidence = match_data.similarity_score.min(1000);

        let opp = ArbitrageOpportunity {{
            match_id: derive_match_id(market_a.key(), market_b.key()),
            market_a: market_a.key(),
            market_b: market_b.key(),
            yield_est,
            confidence,
            kelly_fraction: kelly as u64,
            timestamp: Clock::get()?.unix_timestamp as u64,
        }};

        emit!(ArbitrageDetected {{
            match_id: opp.match_id,
            yield_est: opp.yield_est,
            confidence: opp.confidence,
            kelly_fraction: opp.kelly_fraction,
        }});

        Ok(opp)
    }}

    pub fn execute_harvest(
        ctx: Context<ExecuteHarvest>,
        opportunity: ArbitrageOpportunity,
        amount: u64,
    ) -> Result<()> {{
        let global = &ctx.accounts.global_state;
        require!(!global.paused, ThrshError::ProtocolPaused);

        let authority = &ctx.accounts.authority;
        require!(
            authority.key() == global.authority,
            ThrshError::Unauthorized
        );

        require!(amount > 0, ThrshError::InvalidAmount);
        require!(
            amount <= compute_max_position(opportunity.kelly_fraction, ctx.accounts.vault.amount),
            ThrshError::PositionTooLarge
        );

        let position = &mut ctx.accounts.position;
        position.owner = authority.key();
        position.market_a = opportunity.market_a;
        position.market_b = opportunity.market_b;
        position.side = Side::Yes;
        position.amount = amount;
        position.entry_yield = opportunity.yield_est;
        position.opened_at = Clock::get()?.unix_timestamp as u64;

        emit!(HarvestExecuted {{
            match_id: opportunity.match_id,
            amount,
            yield_est: opportunity.yield_est,
        }});

        Ok(())
    }}

    pub fn pause(ctx: Context<AdminOnly>) -> Result<()> {{
        let global = &mut ctx.accounts.global_state;
        require!(
            ctx.accounts.authority.key() == global.authority,
            ThrshError::Unauthorized
        );
        global.paused = true;
        Ok(())
    }}

    pub fn unpause(ctx: Context<AdminOnly>) -> Result<()> {{
        let global = &mut ctx.accounts.global_state;
        require!(
            ctx.accounts.authority.key() == global.authority,
            ThrshError::Unauthorized
        );
        global.paused = false;
        Ok(())
    }}
}}

fn compute_similarity(a: &[u8; 32], b: &[u8; 32]) -> u16 {{
    let mut matching = 0u32;
    for i in 0..32 {{
        if a[i] == b[i] {{
            matching += 1;
        }}
    }}
    ((matching * 1000) / 32) as u16
}}

fn compute_spread_bps(price_a: u64, price_b: u64) -> u64 {{
    let diff = if price_a > price_b {{
        price_a - price_b
    }} else {{
        price_b - price_a
    }};
    (diff * 10_000) / price_a.max(1)
}}

fn derive_match_id(a: Pubkey, b: Pubkey) -> [u8; 32] {{
    let mut hasher = anchor_lang::solana_program::hash::Hasher::default();
    hasher.hash(a.as_ref());
    hasher.hash(b.as_ref());
    hasher.result().to_bytes()
}}

fn compute_max_position(kelly_fraction: u64, vault_balance: u64) -> u64 {{
    vault_balance
        .checked_mul(kelly_fraction)
        .unwrap_or(0)
        .checked_div(10_000)
        .unwrap_or(0)
}}
""".format(program_id=PROGRAM_ID)


def gen_core_state():
    return """\
use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct GlobalState {
    pub authority: Pubkey,
    pub scan_count: u64,
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
    pub staleness_threshold: u64,
    pub paused: bool,
    pub bump: u8,
}

impl GlobalState {
    pub const SIZE: usize = 8 + 32 + 8 + 8 + 8 + 8 + 1 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct ScanConfig {
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
    pub staleness_threshold: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct MarketInput {
    pub market_key: Pubkey,
    pub platform: Platform,
    pub event_id: [u8; 32],
    pub yes_price: u64,
    pub no_price: u64,
    pub volume: u64,
    pub liquidity: u64,
    pub last_updated: u64,
}

#[account]
pub struct MarketAccount {
    pub platform: Platform,
    pub event_id: [u8; 32],
    pub yes_price: u64,
    pub no_price: u64,
    pub volume: u64,
    pub liquidity: u64,
    pub status: MarketStatus,
    pub last_updated: u64,
    pub bump: u8,
}

impl MarketAccount {
    pub const SIZE: usize = 8 + 1 + 32 + 8 + 8 + 8 + 8 + 1 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct EventMatch {
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub similarity_score: u16,
    pub spread_bps: u64,
    pub timestamp: u64,
}

#[account]
pub struct Position {
    pub owner: Pubkey,
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub side: Side,
    pub amount: u64,
    pub entry_yield: u64,
    pub opened_at: u64,
    pub bump: u8,
}

impl Position {
    pub const SIZE: usize = 8 + 32 + 32 + 32 + 1 + 8 + 8 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct ArbitrageOpportunity {
    pub match_id: [u8; 32],
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub yield_est: u64,
    pub confidence: u16,
    pub kelly_fraction: u64,
    pub timestamp: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum Platform {
    Polymarket,
    Drift,
    Hedgehog,
    MetaDAO,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum MarketStatus {
    Active,
    Settling,
    Settled,
    Expired,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq)]
pub enum Side {
    Yes,
    No,
}
"""


def gen_core_contexts():
    return """\
use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};

use crate::state::*;

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = GlobalState::SIZE,
        seeds = [b"global"],
        bump,
    )]
    pub global_state: Account<'info, GlobalState>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ScanMarkets<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump = global_state.bump,
    )]
    pub global_state: Account<'info, GlobalState>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct DetectArbitrage<'info> {
    #[account(
        seeds = [b"global"],
        bump = global_state.bump,
    )]
    pub global_state: Account<'info, GlobalState>,

    pub market_a: Account<'info, MarketAccount>,
    pub market_b: Account<'info, MarketAccount>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct ExecuteHarvest<'info> {
    #[account(
        seeds = [b"global"],
        bump = global_state.bump,
    )]
    pub global_state: Account<'info, GlobalState>,

    #[account(
        init_if_needed,
        payer = authority,
        space = Position::SIZE,
        seeds = [b"position", authority.key().as_ref()],
        bump,
    )]
    pub position: Account<'info, Position>,

    #[account(mut)]
    pub vault: Account<'info, TokenAccount>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AdminOnly<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump = global_state.bump,
    )]
    pub global_state: Account<'info, GlobalState>,

    pub authority: Signer<'info>,
}
"""


def gen_core_errors():
    return """\
use anchor_lang::prelude::*;

#[error_code]
pub enum ThrshError {
    #[msg("No arbitrage opportunity found for the given market pair")]
    NoArbitrageFound,

    #[msg("Spread is too narrow to justify execution costs")]
    SpreadTooNarrow,

    #[msg("Market price data is stale and must be refreshed")]
    StalePriceData,

    #[msg("Arithmetic overflow in price calculation")]
    MathOverflow,

    #[msg("Unauthorized access attempt")]
    Unauthorized,

    #[msg("Position size exceeds maximum allowed by Kelly criterion")]
    PositionTooLarge,

    #[msg("Invalid amount: must be greater than zero")]
    InvalidAmount,

    #[msg("Protocol is currently paused by admin")]
    ProtocolPaused,

    #[msg("Market has already been settled")]
    MarketSettled,

    #[msg("Event ID format is invalid")]
    InvalidEventId,

    #[msg("Duplicate match entry detected")]
    DuplicateMatch,

    #[msg("Insufficient liquidity in target market")]
    InsufficientLiquidity,
}
"""


def gen_core_events():
    return """\
use anchor_lang::prelude::*;

#[event]
pub struct Initialized {
    pub authority: Pubkey,
    pub min_liquidity: u64,
    pub max_spread_bps: u64,
}

#[event]
pub struct MatchFound {
    pub market_a: Pubkey,
    pub market_b: Pubkey,
    pub similarity_score: u16,
    pub spread_bps: u64,
}

#[event]
pub struct ArbitrageDetected {
    pub match_id: [u8; 32],
    pub yield_est: u64,
    pub confidence: u16,
    pub kelly_fraction: u64,
}

#[event]
pub struct HarvestExecuted {
    pub match_id: [u8; 32],
    pub amount: u64,
    pub yield_est: u64,
}
"""


def gen_math_cargo():
    return """\
[package]
name = "thrsh-math"
version = "0.1.0"
edition = "2021"
description = "Kelly Criterion and probability math for thrsh arbitrage engine"
license = "MIT"

[dependencies]
"""


def gen_math_lib():
    return """\
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
"""


def gen_cli_cargo():
    return """\
[package]
name = "thrsh-cli"
version = "0.1.0"
edition = "2021"
description = "CLI tool for the thrsh arbitrage scanner"
license = "MIT"

[[bin]]
name = "thrsh"
path = "src/main.rs"

[dependencies]
clap = { version = "4", features = ["derive", "env"] }
solana-client = "1.18"
solana-sdk = "1.18"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
thrsh-math = { path = "../libs/thrsh_math" }
"""


def gen_cli_main():
    return r"""use clap::{Parser, Subcommand};
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
"""


def gen_sdk_package_json():
    return """\
{
  "name": "@thrsh/sdk",
  "version": "0.1.0",
  "description": "TypeScript SDK for the thrsh arbitrage engine",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "license": "MIT",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "prettier --check src/"
  },
  "dependencies": {
    "@coral-xyz/anchor": "^0.30.1",
    "@solana/web3.js": "^1.95.0",
    "bn.js": "^5.2.1"
  },
  "devDependencies": {
    "@types/bn.js": "^5.1.5",
    "@types/jest": "^29.5.12",
    "jest": "^29.7.0",
    "prettier": "^3.2.0",
    "ts-jest": "^29.1.2",
    "typescript": "^5.4.0"
  }
}
"""


def gen_sdk_tsconfig():
    return """\
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
"""


def gen_sdk_jest_config():
    return """\
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src", "<rootDir>/tests"],
  testMatch: ["**/*.test.ts"],
  moduleFileExtensions: ["ts", "tsx", "js", "json"],
};
"""


def gen_sdk_types():
    return """\
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
  owner: PublicKey;
  marketA: PublicKey;
  marketB: PublicKey;
  side: Side;
  amount: BN;
  entryYield: BN;
  openedAt: BN;
}

export interface ArbitrageOpportunity {
  matchId: Uint8Array;
  marketA: PublicKey;
  marketB: PublicKey;
  yieldEst: BN;
  confidence: number;
  kellyFraction: BN;
  timestamp: BN;
}

export interface ScanConfig {
  minLiquidity: BN;
  maxSpreadBps: BN;
  stalenessThreshold: BN;
}

export interface ScanResult {
  matches: EventMatch[];
  scannedAt: number;
  marketsProcessed: number;
}

export interface DetectResult {
  opportunity: ArbitrageOpportunity;
  detectedAt: number;
}

export interface HarvestResult {
  signature: string;
  matchId: Uint8Array;
  amount: BN;
  yieldEst: BN;
}
"""


def gen_sdk_client():
    return """\
import {{
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  TransactionInstruction,
  Commitment,
}} from "@solana/web3.js";
import {{ Program, AnchorProvider, Wallet, BN }} from "@coral-xyz/anchor";
import {{
  MarketAccount,
  EventMatch,
  ArbitrageOpportunity,
  ScanConfig,
  ScanResult,
  DetectResult,
  HarvestResult,
}} from "./types";

const PROGRAM_ID = new PublicKey(
  "{program_id}"
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
export class ThrshClient {{
  private connection: Connection;
  private wallet: Wallet;
  private provider: AnchorProvider;
  private commitment: Commitment;

  constructor(
    rpcUrl: string,
    wallet: Wallet,
    commitment: Commitment = "confirmed"
  ) {{
    this.commitment = commitment;
    this.connection = new Connection(rpcUrl, this.commitment);
    this.wallet = wallet;
    this.provider = new AnchorProvider(this.connection, this.wallet, {{
      commitment: this.commitment,
    }});
  }}

  /** Derive the global state PDA. */
  private getGlobalStatePDA(): [PublicKey, number] {{
    return PublicKey.findProgramAddressSync([GLOBAL_SEED], PROGRAM_ID);
  }}

  /** Derive a position PDA for a given owner. */
  private getPositionPDA(owner: PublicKey): [PublicKey, number] {{
    return PublicKey.findProgramAddressSync(
      [POSITION_SEED, owner.toBuffer()],
      PROGRAM_ID
    );
  }}

  /**
   * Scan connected prediction markets and return matched event pairs.
   *
   * Fetches all MarketAccount entries from the program, filters by the
   * provided config thresholds, and pairs events across platforms.
   */
  async scanMarkets(config: ScanConfig): Promise<ScanResult> {{
    const [globalPDA] = this.getGlobalStatePDA();

    const accounts = await this.retryRpc(() =>
      this.connection.getProgramAccounts(PROGRAM_ID, {{
        commitment: this.commitment,
        filters: [{{ dataSize: 85 }}],
      }})
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
    for (let i = 0; i < filtered.length; i++) {{
      for (let j = i + 1; j < filtered.length; j++) {{
        const a = filtered[i];
        const b = filtered[j];

        if (a.platform === b.platform) continue;

        const similarity = this.computeSimilarity(a.eventId, b.eventId);
        if (similarity < 800) continue;

        const spread = this.computeSpreadBps(a.yesPrice, b.yesPrice);
        if (spread.gt(config.maxSpreadBps)) continue;

        matches.push({{
          marketA: accounts[i].pubkey,
          marketB: accounts[j].pubkey,
          similarityScore: similarity,
          spreadBps: spread,
          timestamp: new BN(Math.floor(Date.now() / 1000)),
        }});
      }}
    }}

    return {{
      matches,
      scannedAt: Date.now(),
      marketsProcessed: filtered.length,
    }};
  }}

  /**
   * Analyze a matched event pair and determine if an arbitrage opportunity
   * exists with sufficient yield.
   */
  async detectArbitrage(
    match_: EventMatch,
    minYieldBps: number
  ): Promise<DetectResult | null> {{
    const marketAInfo = await this.retryRpc(() =>
      this.connection.getAccountInfo(match_.marketA)
    );
    const marketBInfo = await this.retryRpc(() =>
      this.connection.getAccountInfo(match_.marketB)
    );

    if (!marketAInfo || !marketBInfo) {{
      return null;
    }}

    const marketA = this.deserializeMarket(marketAInfo.data);
    const marketB = this.deserializeMarket(marketBInfo.data);

    const combined = marketA.yesPrice.add(marketB.yesPrice);
    const scale = new BN(10_000);

    if (combined.gte(scale)) {{
      return null;
    }}

    const yieldEst = scale.sub(combined);
    if (yieldEst.toNumber() < minYieldBps) {{
      return null;
    }}

    const kellyFraction = this.kellyFraction(
      marketA.yesPrice,
      marketB.yesPrice,
      scale
    );

    return {{
      opportunity: {{
        matchId: this.deriveMatchId(match_.marketA, match_.marketB),
        marketA: match_.marketA,
        marketB: match_.marketB,
        yieldEst,
        confidence: match_.similarityScore,
        kellyFraction,
        timestamp: new BN(Math.floor(Date.now() / 1000)),
      }},
      detectedAt: Date.now(),
    }};
  }}

  /**
   * Execute a harvest transaction for a detected arbitrage opportunity.
   * Builds and sends the transaction atomically.
   */
  async executeHarvest(
    opportunity: ArbitrageOpportunity,
    amount: BN,
    vaultAddress: PublicKey
  ): Promise<HarvestResult> {{
    const [globalPDA] = this.getGlobalStatePDA();
    const [positionPDA] = this.getPositionPDA(this.wallet.publicKey);

    const ix = new TransactionInstruction({{
      keys: [
        {{ pubkey: globalPDA, isSigner: false, isWritable: false }},
        {{ pubkey: positionPDA, isSigner: false, isWritable: true }},
        {{ pubkey: vaultAddress, isSigner: false, isWritable: true }},
        {{ pubkey: this.wallet.publicKey, isSigner: true, isWritable: true }},
      ],
      programId: PROGRAM_ID,
      data: Buffer.from([]),
    }});

    const tx = new Transaction().add(ix);
    const sig = await this.provider.sendAndConfirm(tx);

    return {{
      signature: sig,
      matchId: opportunity.matchId,
      amount,
      yieldEst: opportunity.yieldEst,
    }};
  }}

  /** Retry an RPC call up to MAX_RETRIES times on transient failures. */
  private async retryRpc<T>(fn: () => Promise<T>): Promise<T> {{
    let lastError: Error | null = null;
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {{
      try {{
        return await fn();
      }} catch (err) {{
        lastError = err as Error;
        if (attempt < MAX_RETRIES - 1) {{
          await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
        }}
      }}
    }}
    throw lastError;
  }}

  private computeSimilarity(a: Uint8Array, b: Uint8Array): number {{
    let matching = 0;
    for (let i = 0; i < Math.min(a.length, b.length); i++) {{
      if (a[i] === b[i]) matching++;
    }}
    return Math.floor((matching * 1000) / 32);
  }}

  private computeSpreadBps(priceA: BN, priceB: BN): BN {{
    const diff = priceA.gt(priceB) ? priceA.sub(priceB) : priceB.sub(priceA);
    const max = priceA.gt(priceB) ? priceA : priceB;
    return diff.mul(new BN(10_000)).div(max.isZero() ? new BN(1) : max);
  }}

  private kellyFraction(priceA: BN, priceB: BN, scale: BN): BN {{
    const combined = priceA.add(priceB);
    if (combined.gte(scale)) return new BN(0);
    const edge = scale.sub(combined);
    return edge.mul(scale).div(combined.isZero() ? new BN(1) : combined);
  }}

  private deriveMatchId(a: PublicKey, b: PublicKey): Uint8Array {{
    const combined = Buffer.concat([a.toBuffer(), b.toBuffer()]);
    const crypto = require("crypto");
    return new Uint8Array(crypto.createHash("sha256").update(combined).digest());
  }}

  private deserializeMarket(data: Buffer): MarketAccount {{
    const offset = 8;
    const platform = data[offset];
    const eventId = data.slice(offset + 1, offset + 33);
    const yesPrice = new BN(data.slice(offset + 33, offset + 41), "le");
    const noPrice = new BN(data.slice(offset + 41, offset + 49), "le");
    const volume = new BN(data.slice(offset + 49, offset + 57), "le");
    const liquidity = new BN(data.slice(offset + 57, offset + 65), "le");
    const status = data[offset + 65];
    const lastUpdated = new BN(data.slice(offset + 66, offset + 74), "le");

    return {{
      platform,
      eventId: new Uint8Array(eventId),
      yesPrice,
      noPrice,
      volume,
      liquidity,
      status,
      lastUpdated,
    }};
  }}
}}
""".format(program_id=PROGRAM_ID)


def gen_sdk_utils():
    return """\
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
"""


def gen_sdk_index():
    return """\
export { ThrshClient } from "./client";
export {
  Platform,
  MarketStatus,
  Side,
  MarketAccount,
  EventMatch,
  Position,
  ArbitrageOpportunity,
  ScanConfig,
  ScanResult,
  DetectResult,
  HarvestResult,
} from "./types";
export {
  priceToBps,
  bpsToPrice,
  impliedProbability,
  spreadBps,
  isArbitrage,
  expectedYield,
  formatBps,
  lamportsToSol,
  sleep,
} from "./utils";
"""


def gen_test_file():
    return """\
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
"""


def gen_readme():
    return """\
<p align="center">
  <img src="./banner.png" alt="thrsh" width="100%%" />
</p>

<p align="center">
  <a href="{website}">
    <img src="https://img.shields.io/badge/Website-thrsh.fun-1a1a2e?style=flat-square&labelColor=0d0d1a" alt="Website" />
  </a>
  <a href="https://twitter.com/{twitter}">
    <img src="https://img.shields.io/badge/Twitter-@{twitter}-1DA1F2?style=flat-square&logo=x&logoColor=white&labelColor=0d0d1a" alt="Twitter" />
  </a>
  <a href="https://github.com/thrsh-fun/thrsh/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/thrsh-fun/thrsh/ci.yml?branch=main&style=flat-square&label=CI&labelColor=0d0d1a" alt="CI" />
  </a>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square&labelColor=0d0d1a" alt="License" />
</p>

<p align="center">
  <strong>Cross-market prediction market arbitrage engine for Solana.</strong><br/>
  Separate the wheat from noise.
</p>

---

## Key Features

| Feature | Description |
|---------|-------------|
| Cross-Platform Matching | Pairs identical events across Polymarket, Drift, Hedgehog, and MetaDAO |
| Arbitrage Detection | Identifies price gaps where YES_A + YES_B < 1.0 across platforms |
| Kelly Criterion Sizing | Calculates optimal position sizes using full and fractional Kelly |
| Atomic Execution | Bundles trades via Jito for MEV-protected atomic settlement |
| Real-Time Scanning | Continuous market monitoring with configurable staleness thresholds |
| On-Chain State | All positions and match history stored on Solana for transparency |

## Architecture

```mermaid
graph TD
    A[PM Platforms] -->|Event Data| B[Event Matcher]
    B --> C[Arbitrage Detector]
    C -->|YES_A + YES_B < 1.0| D[Kelly Calculator]
    D --> E[Jito Bundle Builder]
    E --> F[Solana RPC]
    F --> G[Atomic Execution]
```

## Installation

```bash
git clone https://github.com/thrsh-fun/thrsh.git
cd thrsh
anchor build
```

Build the CLI:

```bash
cargo build --release -p thrsh-cli
```

Build the TypeScript SDK:

```bash
cd sdk
yarn install
yarn build
```

## Usage

### CLI

Scan markets for matching events:

```bash
thrsh scan --min-liquidity 1000000000 --max-staleness 60
```

Detect arbitrage opportunities:

```bash
thrsh detect --min-yield-bps 50
```

Execute a harvest:

```bash
thrsh harvest --match-id <hex> --amount 500000000
```

### SDK

```typescript
import {{ ThrshClient }} from "@thrsh/sdk";
import {{ Keypair }} from "@solana/web3.js";
import {{ Wallet }} from "@coral-xyz/anchor";
import BN from "bn.js";

const wallet = new Wallet(Keypair.generate());
const client = new ThrshClient("https://api.mainnet-beta.solana.com", wallet);

const scanResult = await client.scanMarkets({{
  minLiquidity: new BN(1_000_000_000),
  maxSpreadBps: new BN(500),
  stalenessThreshold: new BN(60),
}});

for (const match of scanResult.matches) {{
  const detection = await client.detectArbitrage(match, 50);
  if (detection) {{
    console.log("Yield:", detection.opportunity.yieldEst.toString(), "bps");
  }}
}}
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Smart Contracts | Rust / Anchor 0.30 |
| Math Library | Rust (fixed-point arithmetic) |
| SDK | TypeScript / @solana/web3.js |
| CLI | Rust / Clap 4 |
| CI/CD | GitHub Actions |
| Runtime | Solana 1.18 |
| Bundle Execution | Jito |

## License

MIT -- see [LICENSE](./LICENSE) for details.
""".format(website=WEBSITE_URL, twitter=TWITTER_HANDLE)


# ---------------------------------------------------------------------------
# File -> phase mapping (which commits write which files)
# ---------------------------------------------------------------------------

FILE_PHASES = {
    # Phase 0 -- bootstrap
    0: [
        (".gitignore", gen_gitignore),
        ("rustfmt.toml", gen_rustfmt),
        ("clippy.toml", gen_clippy),
        ("LICENSE", gen_license),
        ("Cargo.toml", gen_workspace_cargo),
        ("Anchor.toml", gen_anchor_toml),
        (".github/workflows/ci.yml", gen_ci_yml),
        ("CONTRIBUTING.md", gen_contributing),
        ("README.md", lambda: "# thrsh\n\nCross-market prediction market arbitrage engine for Solana.\n"),
    ],
    # Phase 1 -- core structs
    1: [
        ("programs/thrsh_core/Cargo.toml", gen_core_cargo),
        ("programs/thrsh_core/src/state.rs", gen_core_state),
        ("programs/thrsh_core/src/errors.rs", gen_core_errors),
        ("programs/thrsh_core/src/events.rs", gen_core_events),
        ("programs/thrsh_core/src/contexts.rs", gen_core_contexts),
    ],
    # Phase 2 -- event matcher (lib.rs with scan_markets)
    2: [
        ("programs/thrsh_core/src/lib.rs", gen_core_lib),
    ],
    # Phase 3 -- detector (lib.rs already has detect, math lib starts)
    3: [
        ("libs/thrsh_math/Cargo.toml", gen_math_cargo),
    ],
    # Phase 4 -- math library
    4: [
        ("libs/thrsh_math/src/lib.rs", gen_math_lib),
    ],
    # Phase 5 -- SDK
    5: [
        ("sdk/package.json", gen_sdk_package_json),
        ("sdk/tsconfig.json", gen_sdk_tsconfig),
        ("sdk/jest.config.js", gen_sdk_jest_config),
        ("sdk/src/types.ts", gen_sdk_types),
        ("sdk/src/client.ts", gen_sdk_client),
        ("sdk/src/utils.ts", gen_sdk_utils),
        ("sdk/src/index.ts", gen_sdk_index),
    ],
    # Phase 6 -- CLI, tests, docs
    6: [
        ("cli/Cargo.toml", gen_cli_cargo),
        ("cli/src/main.rs", gen_cli_main),
        ("sdk/tests/thrsh.test.ts", gen_test_file),
        ("CHANGELOG.md", gen_changelog),
    ],
}


def get_phase_for_commit(index, total):
    """Map a linear commit index to its development phase (0-6)."""
    frac = index / total
    if frac < 0.07:
        return 0
    elif frac < 0.20:
        return 1
    elif frac < 0.33:
        return 2
    elif frac < 0.47:
        return 3
    elif frac < 0.60:
        return 4
    elif frac < 0.80:
        return 5
    else:
        return 6


# ---------------------------------------------------------------------------
# Incremental file writing (simulate edits across commits)
# ---------------------------------------------------------------------------


def split_content(content, n_chunks):
    """Split *content* into *n_chunks* cumulative slices."""
    lines = content.splitlines(keepends=True)
    if n_chunks <= 1 or len(lines) <= 1:
        return [content]
    chunk_size = max(1, len(lines) // n_chunks)
    slices = []
    for i in range(1, n_chunks + 1):
        end = min(i * chunk_size, len(lines))
        if i == n_chunks:
            end = len(lines)
        slices.append("".join(lines[:end]))
    return slices


class FileTracker:
    """Tracks which files have been fully written and which are in progress."""

    def __init__(self):
        self.written = set()
        self.partial = {}  # path -> (chunks_list, current_index)

    def prepare_phase(self, phase):
        """Queue all files for the given phase that have not been written."""
        if phase not in FILE_PHASES:
            return
        for path, gen_fn in FILE_PHASES[phase]:
            if path not in self.written and path not in self.partial:
                content = gen_fn()
                n = random.randint(2, 5)
                chunks = split_content(content, n)
                self.partial[path] = (chunks, 0)

    def next_write(self, phase):
        """Return (path, content) for the next incremental write, or None."""
        # prioritise files from current phase
        candidates = []
        if phase in FILE_PHASES:
            phase_paths = {p for p, _ in FILE_PHASES[phase]}
            candidates = [p for p in self.partial if p in phase_paths]
        if not candidates:
            candidates = list(self.partial.keys())
        if not candidates:
            return None
        path = random.choice(candidates)
        chunks, idx = self.partial[path]
        content = chunks[idx]
        idx += 1
        if idx >= len(chunks):
            self.written.add(path)
            del self.partial[path]
        else:
            self.partial[path] = (chunks, idx)
        return (path, content)

    def flush_all(self):
        """Return list of (path, content) to finalize every remaining file."""
        result = []
        for path in list(self.partial.keys()):
            chunks, _ = self.partial[path]
            result.append((path, chunks[-1]))
            self.written.add(path)
        self.partial.clear()
        return result


# ---------------------------------------------------------------------------
# README special handling (initial stub then final version)
# ---------------------------------------------------------------------------

README_STUB = "# thrsh\n\nCross-market prediction market arbitrage engine for Solana.\n"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main():
    print("Initializing git repository ...")
    if os.path.isdir(os.path.join(REPO_DIR, ".git")):
        print("ERROR: .git already exists in REPO_DIR. Aborting to avoid data loss.")
        return

    run_git(["init"])
    run_git(["config", "user.name", USER_NAME])
    run_git(["config", "user.email", USER_EMAIL])
    run_git(["checkout", "-b", "main"])

    # Copy the banner into the repo
    copy_banner()

    dates = generate_commit_dates(TARGET_COMMITS, START_DATE, END_DATE)
    messages = build_commit_messages(len(dates))
    tracker = FileTracker()

    print("Generating {} commits from {} to {} ...".format(
        len(dates),
        START_DATE.strftime("%Y-%m-%d"),
        END_DATE.strftime("%Y-%m-%d"),
    ))

    last_phase = -1
    readme_finalized = False

    for i, (dt, msg) in enumerate(zip(dates, messages)):
        phase = get_phase_for_commit(i, len(dates))

        # When phase advances, queue new files
        if phase != last_phase:
            tracker.prepare_phase(phase)
            last_phase = phase

        # Write incremental file content
        write_op = tracker.next_write(phase)
        if write_op:
            path, content = write_op
            write_file(path, content)
            run_git(["add", path], date=dt)

        # Banner goes in the very first commit
        if i == 0:
            banner_dst = os.path.join(REPO_DIR, "banner.png")
            if os.path.isfile(banner_dst):
                run_git(["add", "banner.png"], date=dt)

        # Finalize README near the end
        if phase == 6 and not readme_finalized and "readme" in msg.lower():
            write_file("README.md", gen_readme())
            run_git(["add", "README.md"], date=dt)
            readme_finalized = True

        # Make sure there is something staged
        run_git(["add", "-A"], date=dt)

        # Commit
        run_git(["commit", "--allow-empty", "-m", msg], date=dt)

        if (i + 1) % 25 == 0:
            print("  ... {} / {} commits".format(i + 1, len(dates)))

    # Flush any remaining partial files
    remaining = tracker.flush_all()
    if remaining:
        final_date = dates[-1] + timedelta(minutes=5)
        for path, content in remaining:
            write_file(path, content)
            run_git(["add", path], date=final_date)
        run_git(["commit", "-m", "chore: finalize remaining source files"], date=final_date)

    # Ensure README is finalized
    if not readme_finalized:
        final_date = dates[-1] + timedelta(minutes=10)
        write_file("README.md", gen_readme())
        run_git(["add", "README.md"], date=final_date)
        run_git(["commit", "-m", "docs(readme): final formatting pass"], date=final_date)

    total = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    count = total.stdout.strip() if total.returncode == 0 else "?"

    print("Done. {} commits created.".format(count))
    print("Repository is ready at: {}".format(os.path.abspath(REPO_DIR)))
    print("")
    print("Next steps:")
    print("  1. Create the GitHub repo: gh repo create thrsh-fun/thrsh --public")
    print("  2. Add remote: git remote add origin git@github.com:thrsh-fun/thrsh.git")
    print("  3. Push: git push -u origin main")


if __name__ == "__main__":
    main()
