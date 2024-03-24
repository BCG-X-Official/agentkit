-- Create table
CREATE TABLE COMMITS (
    commit_hash TEXT,
    commit_timestamp TIMESTAMP,
    commit_user TEXT,
    commit_message TEXT,
    file_changed TEXT
);

-- Copy CSV
COPY COMMITS (commit_hash, commit_timestamp, commit_user, commit_message, file_changed)
FROM '/docker-entrypoint-initdb.d/commit_history.csv'
WITH CSV HEADER;