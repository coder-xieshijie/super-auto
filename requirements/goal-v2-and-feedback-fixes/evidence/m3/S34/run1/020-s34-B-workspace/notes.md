1. Rust guarantees memory safety without a garbage collector, using compile-time ownership and borrowing rules.
2. Rust has no null references; absence of a value is modeled explicitly with the `Option` enum.
3. Fallible operations return the `Result` enum instead of throwing exceptions.
4. The borrow checker prevents data races at compile time, enabling fearless concurrency.
5. Rust's type system supports algebraic subtyping, encoding product and sum types in the type itself.
6. Zero-cost abstractions mean traits, generics, and iterators add no runtime overhead.
7. The `cargo` build tool and the crates.io registry form the official build and dependency ecosystem.
8. Rust compiles to native machine code through LLVM, with no mandatory runtime or garbage collector.
9. Pattern matching via `match` and destructuring `let` is a first-class, exhaustively checked control flow feature.
10. Rust was first released in 2010, reached version 1.0 in May 2015, and is stewarded by the Rust Foundation.
