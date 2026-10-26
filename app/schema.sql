CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 120),
    description TEXT NOT NULL DEFAULT '' CHECK (length(description) <= 2000),
    is_done INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;

CREATE INDEX IF NOT EXISTS idx_tasks_is_done ON tasks (is_done);
