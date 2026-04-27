CREATE TABLE IF NOT EXISTS notifications_v2 (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  related_project_id TEXT NOT NULL DEFAULT '',
  related_work_item_id TEXT NOT NULL DEFAULT '',
  related_document_id TEXT NOT NULL DEFAULT '',
  is_read INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_v2_user ON notifications_v2(user_id, is_read);

CREATE TABLE IF NOT EXISTS audit_logs_v2 (
  id TEXT PRIMARY KEY,
  actor_user_id TEXT NOT NULL,
  action_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_v2_actor ON audit_logs_v2(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_v2_entity ON audit_logs_v2(entity_type, entity_id);

CREATE TABLE IF NOT EXISTS reports_v2 (
  id TEXT PRIMARY KEY,
  report_type TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT '',
  project_id TEXT NOT NULL DEFAULT '',
  period_start TEXT NOT NULL DEFAULT '',
  period_end TEXT NOT NULL DEFAULT '',
  content_json TEXT NOT NULL DEFAULT '{}',
  generated_at INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'generated'
);

CREATE INDEX IF NOT EXISTS idx_reports_v2_type ON reports_v2(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_v2_user ON reports_v2(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_v2_project ON reports_v2(project_id);

CREATE TABLE IF NOT EXISTS report_comments_v2 (
  id TEXT PRIMARY KEY,
  report_id TEXT NOT NULL,
  commented_by TEXT NOT NULL,
  comment TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_report_comments_v2_report ON report_comments_v2(report_id);
