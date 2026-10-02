1. Rust is a systems programming language focused on speed, memory safety, and thread safety, sponsored by Mozilla and now stewarded by the Rust Foundation.
2. It first appeared publicly in 2010, reached 1.0 in May 2015, and has shipped stable releases roughly every six weeks since.
3. Ownership, borrowing, and lifetimes enforce memory safety at compile time without requiring a garbage collector.
4. Rust guarantees memory safety but not full thread safety, which is why it uses `Send` and `Sync` traits plus types like `Arc` and `Mutex` to coordinate concurrent access.
5. The borrow checker permits either many immutable references or one mutable reference to a value at a time, a rule called "aliasing XOR mutability".
6. Trait-based generics with monomorphization give Rust zero-cost abstraction, producing native machine code with no runtime type metadata.
7. Cargo is Rust's built-in build tool and package manager, and crates.io is its central registry for published libraries called crates.
8. Rust's error handling splits recoverable failures into `Result<T, E>` and unrecoverable ones into the `panic!` macro.
9. It targets LLVM for compilation and can also be built on the alternative rustc_codegen_cranelift backend for faster builds.
10. `unsafe` blocks let programmers opt out of the borrow checker for low-level work while requiring the same safety invariants to be upheld manually.
