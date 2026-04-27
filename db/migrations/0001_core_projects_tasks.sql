CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  owner_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'planning',
  start_date TEXT NOT NULL DEFAULT '',
  due_date TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS project_members (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role_in_project TEXT NOT NULL DEFAULT 'member',
  joined_at INTEGER NOT NULL,
  UNIQUE(project_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_project_members_project ON project_members(project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_user ON project_members(user_id);

CREATE TABLE IF NOT EXISTS work_items (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  priority TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'todo',
  due_date TEXT NOT NULL DEFAULT '',
  created_by TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  dependencies_json TEXT NOT NULL DEFAULT '[]',
  collaborators_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id);
CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);
CREATE INDEX IF NOT EXISTS idx_work_items_due_date ON work_items(due_date);

CREATE TABLE IF NOT EXISTS work_item_assignees (
  id TEXT PRIMARY KEY,
  work_item_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  assigned_at INTEGER NOT NULL,
  UNIQUE(work_item_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_work_item_assignees_item ON work_item_assignees(work_item_id);
CREATE INDEX IF NOT EXISTS idx_work_item_assignees_user ON work_item_assignees(user_id);

CREATE TABLE IF NOT EXISTS work_item_feedback (
  id TEXT PRIMARY KEY,
  work_item_id TEXT NOT NULL,
  submitted_by TEXT NOT NULL,
  completion_summary TEXT NOT NULL DEFAULT '',
  blockers TEXT NOT NULL DEFAULT '',
  next_steps TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_work_item_feedback_item ON work_item_feedback(work_item_id);
