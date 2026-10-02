1. Rust is a systems programming language focused on safety, speed, and concurrency, with no garbage collector.
2. Ownership is Rust's core memory-management model: every value has a single owner, and ownership transfers when the value is moved.
3. Borrowing lets Rust functions take references to values without taking ownership, checked at compile time by the borrow checker.
4. Rust guarantees memory safety without a garbage collector because dangling pointers, double frees, and data races are rejected at compile time.
5. Rust's `cargo` tool handles building, dependency management, testing, and documentation from one integrated project layout.
6. `rustc` compiles Rust to native machine code directly, and `rustup` manages multiple toolchain versions including nightly compiler features.
7. Crates.io is Rust's official package registry, and Cargo.lock records exact dependency versions for reproducible builds.
8. Rust has no built-in garbage-collected runtime or mandatory runtime, making it suitable for operating systems, embedded systems, and WebAssembly.
9. Pattern matching appears throughout Rust syntax, powering `match`, destructuring in `let`, and exhaustive handling of enum variants.
10. Rust 2015 edition and the newer 2018, 2021, and 2024 editions give projects explicit control over language features and migration.
