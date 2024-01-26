-- Create tables
CREATE TABLE COMMITS (
    commit_hash TEXT,
    commit_timestamp TIMESTAMP,
    commit_user TEXT,
    commit_message TEXT,
    file_changed TEXT
);

CREATE TABLE PULL_REQUESTS (
    pr_number INT,
    pr_title TEXT,
    pr_state TEXT,
    pr_user TEXT,
    pr_created_at TIMESTAMP,
    pr_updated_at TIMESTAMP,
    pr_closed_at TIMESTAMP,
    pr_merged_at TIMESTAMP,
    pr_merged BOOLEAN,
    pr_num_additions BIGINT,
    pr_num_deletions BIGINT,
    pr_num_changed_files INT,
    pr_num_comments INT,
    pr_num_review_comments INT,
    pr_num_commits INT,
    pr_mergeable BOOLEAN,
    pr_mergeable_state TEXT
);

CREATE TABLE ISSUES (
    issue_number INT,
    issue_title TEXT,
    issue_state TEXT,
    issue_author TEXT,
    issue_created_at TIMESTAMP,
    issue_last_updated TIMESTAMP,
    issue_num_comments INT
);

-- Copy CSVs
COPY COMMITS (commit_hash, commit_timestamp, commit_user, commit_message, file_changed)
FROM '/docker-entrypoint-initdb.d/commit_history.csv'
WITH CSV HEADER;

COPY PULL_REQUESTS (
    pr_number, pr_title, pr_state, pr_user, pr_created_at, pr_updated_at,
    pr_closed_at, pr_merged_at, pr_merged, pr_num_additions, pr_num_deletions,
    pr_num_changed_files, pr_num_comments, pr_num_review_comments, pr_num_commits,
    pr_mergeable, pr_mergeable_state)
FROM '/docker-entrypoint-initdb.d/pull_requests.csv'  -- Adjust the file name/path as necessary
WITH CSV HEADER;

COPY ISSUES (issue_number, issue_title, issue_state, issue_author, issue_created_at, issue_last_updated, issue_num_comments)
FROM '/docker-entrypoint-initdb.d/issues.csv'
WITH CSV HEADER;
