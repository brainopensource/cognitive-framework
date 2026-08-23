.PHONY: test check build lint clean bench run

test:
	cargo test

check:
	cargo check

build:
	cargo build --release

lint:
	cargo clippy --all-targets --all-features -- -D warnings

clean:
	cargo clean
	rm -rf output/*.json output/*.jsonl /tmp/lex_sandbox_* /tmp/lex_test_slice_*

run:
	cargo run -- "Create an async TokenBucket limiter"
