1. Rust is a systems programming language focused on speed, memory safety, and thread safety.
2. Rust was first publicly released in 2010 and reached its 1.0 stable version in May 2015.
3. Rust's central innovation is ownership: every value has exactly one owner at compile time.
4. When ownership ends, Rust automatically runs the value's destructor through a mechanism called drop.
5. Borrowing lets a value be referenced temporarily, with rules enforced at compile time to prevent dangling references.
6. The borrow checker guarantees at compile time that no two references allow conflicting mutation or mutation during read.
7. Rust has no garbage collector; memory is freed deterministically at the end of a value's lifetime.
8. Rust guarantees memory safety without a garbage collector or reference counting.
9. Cargo is Rust's official build tool and package manager, handling dependencies, building, testing, and documentation.
10. Rust is used for operating systems, embedded systems, web backends, and browsers such as Firefox and Chrome components.
