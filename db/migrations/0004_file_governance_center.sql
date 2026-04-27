CREATE TABLE IF NOT EXISTS file_records_v2 (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  project_id TEXT NOT NULL DEFAULT '',
  work_item_id TEXT NOT NULL DEFAULT '',
  workspace_id TEXT NOT NULL DEFAULT 'work-chat',
  department TEXT NOT NULL DEFAULT '',
  owner_user_id TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'general',
  status TEXT NOT NULL DEFAULT 'draft',
  source_module TEXT NOT NULL DEFAULT 'file-center',
  source_ref_id TEXT NOT NULL DEFAULT '',
  current_version_id TEXT NOT NULL DEFAULT '',
  is_signed INTEGER NOT NULL DEFAULT 0,
  is_locked INTEGER NOT NULL DEFAULT 0,
  is_encrypted INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_file_records_v2_project ON file_records_v2(project_id);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_work_item ON file_records_v2(work_item_id);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_workspace ON file_records_v2(workspace_id);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_owner ON file_records_v2(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_status ON file_records_v2(status);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_category ON file_records_v2(category);
CREATE INDEX IF NOT EXISTS idx_file_records_v2_updated_at ON file_records_v2(updated_at);

CREATE TABLE IF NOT EXISTS file_versions_v2 (
  id TEXT PRIMARY KEY,
  file_id TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  filename TEXT NOT NULL,
  mime TEXT NOT NULL DEFAULT 'application/octet-stream',
  size INTEGER NOT NULL DEFAULT 0,
  storage_path TEXT NOT NULL DEFAULT '',
  checksum_sha256 TEXT NOT NULL DEFAULT '',
  change_summary TEXT NOT NULL DEFAULT '',
  created_by TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  derived_from_version_id TEXT NOT NULL DEFAULT '',
  is_signed_snapshot INTEGER NOT NULL DEFAULT 0,
  signed_by TEXT NOT NULL DEFAULT '',
  signed_at INTEGER NOT NULL DEFAULT 0,
  is_locked_snapshot INTEGER NOT NULL DEFAULT 0,
  is_encrypted_snapshot INTEGER NOT NULL DEFAULT 0,
  UNIQUE(file_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_file_versions_v2_file ON file_versions_v2(file_id);
CREATE INDEX IF NOT EXISTS idx_file_versions_v2_created_at ON file_versions_v2(created_at);

CREATE TABLE IF NOT EXISTS file_workflows_v2 (
  id TEXT PRIMARY KEY,
  file_id TEXT NOT NULL,
  project_id TEXT NOT NULL DEFAULT '',
  work_item_id TEXT NOT NULL DEFAULT '',
  workspace_id TEXT NOT NULL DEFAULT 'work-chat',
  workflow_type TEXT NOT NULL DEFAULT 'review_approve_sign',
  status TEXT NOT NULL DEFAULT 'active',
  initiated_by TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  closed_at INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_file_workflows_v2_file ON file_workflows_v2(file_id);
CREATE INDEX IF NOT EXISTS idx_file_workflows_v2_project ON file_workflows_v2(project_id);
CREATE INDEX IF NOT EXISTS idx_file_workflows_v2_status ON file_workflows_v2(status);

CREATE TABLE IF NOT EXISTS file_workflow_steps_v2 (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  step_type TEXT NOT NULL,
  sequence_order INTEGER NOT NULL DEFAULT 1,
  assigned_user_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  comments TEXT NOT NULL DEFAULT '',
  acted_at INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_file_workflow_steps_v2_workflow ON file_workflow_steps_v2(workflow_id);
CREATE INDEX IF NOT EXISTS idx_file_workflow_steps_v2_assigned ON file_workflow_steps_v2(assigned_user_id, status);

CREATE TABLE IF NOT EXISTS file_archives_v2 (
  id TEXT PRIMARY KEY,
  file_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  archive_path TEXT NOT NULL,
  encryption_method TEXT NOT NULL DEFAULT 'xor-sha256',
  key_ref TEXT NOT NULL DEFAULT 'local-default',
  locked_at INTEGER NOT NULL,
  locked_by TEXT NOT NULL,
  retention_class TEXT NOT NULL DEFAULT 'standard',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_file_archives_v2_file ON file_archives_v2(file_id);
CREATE INDEX IF NOT EXISTS idx_file_archives_v2_version ON file_archives_v2(version_id);

CREATE TABLE IF NOT EXISTS file_access_grants_v2 (
  id TEXT PRIMARY KEY,
  granted_by TEXT NOT NULL,
  granted_user_id TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  permission TEXT NOT NULL DEFAULT 'read',
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL,
  revoked_at INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_file_access_grants_v2_user ON file_access_grants_v2(granted_user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_file_access_grants_v2_scope ON file_access_grants_v2(scope_type, scope_id);

CREATE TABLE IF NOT EXISTS file_tags_v2 (
  id TEXT PRIMARY KEY,
  file_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_file_tags_v2_file ON file_tags_v2(file_id);
CREATE INDEX IF NOT EXISTS idx_file_tags_v2_tag ON file_tags_v2(tag);

CREATE TABLE IF NOT EXISTS file_daily_digest_state_v2 (
  id TEXT PRIMARY KEY,
  digest_date TEXT NOT NULL UNIQUE,
  last_run_at INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'ok',
  error_message TEXT NOT NULL DEFAULT ''
);

