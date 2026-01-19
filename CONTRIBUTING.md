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
