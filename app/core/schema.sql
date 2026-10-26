CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 120),
    description TEXT NOT NULL DEFAULT '' CHECK (length(description) <= 2000),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'scheduled', 'in_progress', 'done')),
    priority INTEGER NOT NULL DEFAULT 0 CHECK (priority BETWEEN 0 AND 3),
    due_at TEXT CHECK (due_at IS NULL OR length(due_at) = 16),
    completed_at TEXT CHECK (completed_at IS NULL OR length(completed_at) = 19),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(name) BETWEEN 1 AND 24)
) STRICT;

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
) STRICT;

CREATE TABLE IF NOT EXISTS subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 120),
    is_done INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1))
) STRICT;

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    body TEXT NOT NULL CHECK (length(body) BETWEEN 1 AND 1000),
    created_at TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    url TEXT NOT NULL CHECK (length(url) BETWEEN 1 AND 500 AND (url LIKE 'https://%' OR url LIKE 'http://%')),
    label TEXT NOT NULL DEFAULT '' CHECK (length(label) <= 80)
) STRICT;

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    original_name TEXT NOT NULL CHECK (length(original_name) BETWEEN 1 AND 120),
    stored_name TEXT NOT NULL UNIQUE CHECK (length(stored_name) BETWEEN 33 AND 37),
    mime_type TEXT NOT NULL CHECK (mime_type IN ('application/pdf', 'image/png', 'image/jpeg')),
    size INTEGER NOT NULL CHECK (size BETWEEN 1 AND 5242880),
    created_at TEXT NOT NULL
) STRICT;

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_at ON tasks (due_at);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag ON task_tags (tag_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_task ON subtasks (task_id);
CREATE INDEX IF NOT EXISTS idx_comments_task ON comments (task_id);
CREATE INDEX IF NOT EXISTS idx_links_task ON links (task_id);
CREATE INDEX IF NOT EXISTS idx_attachments_task ON attachments (task_id);

PRAGMA user_version = 2;
