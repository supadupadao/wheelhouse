migrate:
	cargo run --manifest-path ./migration/Cargo.toml -- up

generate:
	sea-orm-cli generate entity -o ./entities/src --lib
