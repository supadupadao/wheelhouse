CREATE TABLE IF NOT EXISTS wallet (
    address BYTEA PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS dao (
    address BYTEA PRIMARY KEY,
    jetton_master BYTEA UNIQUE
);

CREATE TABLE IF NOT EXISTS proposal (
    address BYTEA PRIMARY KEY,
    dao BYTEA NOT NULL REFERENCES dao(address),
    id INT NOT NULL,
    is_initialized BOOLEAN NOT NULL,
    is_executed BOOLEAN NOT NULL,
    votes_yes NUMERIC(39, 0) NOT NULL DEFAULT 0,
    votes_no NUMERIC(39, 0) NOT NULL DEFAULT 0,
    expires_at BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS vote (
    proposal BYTEA NOT NULL REFERENCES proposal(address),
    wallet BYTEA NOT NULL REFERENCES wallet(address),
    PRIMARY KEY (proposal, wallet)
);

CREATE TABLE IF NOT EXISTS jetton_wallet (
    jetton_master BYTEA NOT NULL REFERENCES dao(jetton_master),
    wallet BYTEA NOT NULL REFERENCES wallet(address),
    balance NUMERIC(39, 0) NOT NULL DEFAULT 0,
    PRIMARY KEY (jetton_master, wallet)
);

CREATE TABLE IF NOT EXISTS trace_log (
    address BYTEA NOT NULL,
    hash TEXT NOT NULL,
    utime BIGINT NOT NULL,
    PRIMARY KEY (address, hash)
);
