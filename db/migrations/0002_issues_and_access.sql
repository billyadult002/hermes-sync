CREATE TABLE IF NOT EXISTS project_issues (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  work_item_id TEXT NOT NULL DEFAULT '',
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  severity TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'open',
  reported_by TEXT NOT NULL,
  assigned_to TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  resolved_at INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_issues_project ON project_issues(project_id);
CREATE INDEX IF NOT EXISTS idx_project_issues_status ON project_issues(status);
CREATE INDEX IF NOT EXISTS idx_project_issues_severity ON project_issues(severity);
CREATE INDEX IF NOT EXISTS idx_project_issues_assigned_to ON project_issues(assigned_to);

CREATE TABLE IF NOT EXISTS access_grants (
  id TEXT PRIMARY KEY,
  granted_by_admin_id TEXT NOT NULL,
  granted_user_id TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  permission TEXT NOT NULL DEFAULT 'read',
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL,
  revoked_at INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_access_grants_user ON access_grants(granted_user_id);
CREATE INDEX IF NOT EXISTS idx_access_grants_scope ON access_grants(scope_type, scope_id);
