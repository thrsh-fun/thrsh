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
