CREATE TABLE IF NOT EXISTS dao (
    address BYTEA PRIMARY KEY,
    jetton_master BYTEA NOT NULL UNIQUE,
    jetton_name TEXT NOT NULL,
    jetton_symbol TEXT NOT NULL,
    jetton_icon_url TEXT,
    jetton_description TEXT
);

CREATE TABLE IF NOT EXISTS dao_participant (
	dao BYTEA NOT NULL REFERENCES dao(address),
    address BYTEA NOT NULL,
    jetton_wallet BYTEA NOT NULL,
    lock_address BYTEA,
    PRIMARY KEY (dao, address)
);

CREATE TABLE IF NOT EXISTS proposal (
    address BYTEA PRIMARY KEY,
    dao BYTEA NOT NULL REFERENCES dao(address),
    id INT NOT NULL,
    is_initialized BOOLEAN NOT NULL,
    is_executed BOOLEAN NOT NULL,
    votes_yes NUMERIC(39, 0) NOT NULL DEFAULT 0,
    votes_no NUMERIC(39, 0) NOT NULL DEFAULT 0,
    expires_at BIGINT NOT NULL,

    --- Payload
    receiver BYTEA NOT NULL,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jetton_wallet (
    address BYTEA NOT NULL,
    jetton_master BYTEA NOT NULL REFERENCES dao(jetton_master),
    owner BYTEA NOT NULL,
    balance NUMERIC(39, 0) NOT NULL DEFAULT 0,
    PRIMARY KEY (jetton_master, address)
);

CREATE TABLE IF NOT EXISTS trace_log (
    address BYTEA NOT NULL,
    hash TEXT NOT NULL,
    utime BIGINT NOT NULL,
    PRIMARY KEY (address, hash)
);
