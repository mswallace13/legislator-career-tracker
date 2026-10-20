CREATE TABLE IF NOT EXISTS legislators (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    chamber TEXT NOT NULL,
    party TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    legislator_id TEXT,
    degree TEXT,
    institution TEXT,
    FOREIGN KEY(legislator_id) REFERENCES legislators(id)
);

CREATE TABLE IF NOT EXISTS professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    legislator_id TEXT,
    job_title TEXT,
    category TEXT,
    FOREIGN KEY(legislator_id) REFERENCES legislators(id)
);

CREATE TABLE IF NOT EXISTS military_service (
    legislator_id TEXT PRIMARY KEY,
    branch TEXT,
    highest_rank TEXT,
    veteran_status BOOLEAN,
    FOREIGN KEY(legislator_id) REFERENCES legislators(id)
);