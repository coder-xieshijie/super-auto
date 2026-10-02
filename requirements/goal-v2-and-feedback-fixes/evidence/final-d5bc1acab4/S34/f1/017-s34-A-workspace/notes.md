1. Rust is a systems programming language focused on speed, memory safety, and thread safety.
2. Rust guarantees memory safety without a garbage collector, using ownership and borrowing checked at compile time.
3. Every value in Rust has a single owner, and ownership is transferred or borrowed rather than shared freely.
4. The borrow checker allows either many immutable references or exactly one mutable reference, never both at once.
5. Lifetimes are tracked by the compiler so references never outlive the data they point to.
6. Rust's compiler errors are famously detailed, often suggesting fixes directly in the diagnostic message.
7. Cargo is Rust's official build tool and package manager, handling dependencies, building, testing, and documentation.
8. Rust's standard library is small, with many features coming from community crates such as serde and tokio.
9. Rust can call C code through the FFI, and its compiled output interoperates with most C-based toolchains.
10. Rust powers tools like ripgrep, the Linux kernel's experimental drivers, and WebAssembly components.
