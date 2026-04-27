CREATE TABLE IF NOT EXISTS project_chat_conversations_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active',
  created_by TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_chat_conversations_v2_project
  ON project_chat_conversations_v2(project_id, updated_at);

CREATE TABLE IF NOT EXISTS project_chat_messages_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  conversation_id TEXT NOT NULL DEFAULT '',
  sender_id TEXT NOT NULL DEFAULT '',
  sender_name TEXT NOT NULL DEFAULT '',
  message_type TEXT NOT NULL DEFAULT 'text',
  content TEXT NOT NULL DEFAULT '',
  lifecycle_status TEXT NOT NULL DEFAULT 'active',
  is_key_message INTEGER NOT NULL DEFAULT 0,
  is_system_message INTEGER NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  archived_at INTEGER NOT NULL DEFAULT 0,
  soft_deleted_at INTEGER NOT NULL DEFAULT 0,
  hard_deleted_at INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_project_chat_messages_v2_project_created
  ON project_chat_messages_v2(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_chat_messages_v2_project_lifecycle
  ON project_chat_messages_v2(project_id, lifecycle_status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_chat_messages_v2_project_key
  ON project_chat_messages_v2(project_id, is_key_message, created_at DESC);

CREATE TABLE IF NOT EXISTS project_chat_summaries_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  summary_version INTEGER NOT NULL DEFAULT 1,
  summary_type TEXT NOT NULL DEFAULT 'manual',
  summary_status TEXT NOT NULL DEFAULT 'generated',
  summary_content_text TEXT NOT NULL DEFAULT '',
  main_progress_json TEXT NOT NULL DEFAULT '[]',
  confirmed_decisions_json TEXT NOT NULL DEFAULT '[]',
  task_updates_json TEXT NOT NULL DEFAULT '[]',
  file_updates_json TEXT NOT NULL DEFAULT '[]',
  issues_risks_json TEXT NOT NULL DEFAULT '[]',
  next_actions_json TEXT NOT NULL DEFAULT '[]',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  source_message_start_id TEXT NOT NULL DEFAULT '',
  source_message_end_id TEXT NOT NULL DEFAULT '',
  source_message_count INTEGER NOT NULL DEFAULT 0,
  provider_type TEXT NOT NULL DEFAULT 'rule_based',
  provider_metadata_json TEXT NOT NULL DEFAULT '{}',
  generation_trigger TEXT NOT NULL DEFAULT 'manual',
  generated_by TEXT NOT NULL DEFAULT '',
  generated_at INTEGER NOT NULL,
  quality_score REAL NOT NULL DEFAULT 0,
  is_current INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_project_chat_summaries_v2_project_generated
  ON project_chat_summaries_v2(project_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_chat_summaries_v2_project_current
  ON project_chat_summaries_v2(project_id, is_current, generated_at DESC);

CREATE TABLE IF NOT EXISTS project_chat_summary_runs_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  trigger_type TEXT NOT NULL DEFAULT 'manual',
  provider_type TEXT NOT NULL DEFAULT 'rule_based',
  status TEXT NOT NULL DEFAULT 'queued',
  started_at INTEGER NOT NULL DEFAULT 0,
  completed_at INTEGER NOT NULL DEFAULT 0,
  summary_id TEXT NOT NULL DEFAULT '',
  error_message TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_chat_summary_runs_v2_project_status
  ON project_chat_summary_runs_v2(project_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_chat_summary_runs_v2_status
  ON project_chat_summary_runs_v2(status, created_at DESC);

CREATE TABLE IF NOT EXISTS project_chat_retention_policies_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL DEFAULT '',
  scope_type TEXT NOT NULL DEFAULT 'global',
  archive_after_days INTEGER NOT NULL DEFAULT 14,
  soft_delete_after_days INTEGER NOT NULL DEFAULT 30,
  hard_delete_after_days INTEGER NOT NULL DEFAULT 90,
  retain_key_messages INTEGER NOT NULL DEFAULT 1,
  retain_system_messages INTEGER NOT NULL DEFAULT 1,
  retain_approval_related_messages INTEGER NOT NULL DEFAULT 1,
  retain_file_change_messages INTEGER NOT NULL DEFAULT 1,
  allow_restore_from_archive INTEGER NOT NULL DEFAULT 1,
  allow_restore_from_soft_delete INTEGER NOT NULL DEFAULT 0,
  created_by TEXT NOT NULL DEFAULT 'system',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_project_chat_retention_policies_v2_unique_scope
  ON project_chat_retention_policies_v2(scope_type, project_id);
CREATE INDEX IF NOT EXISTS idx_project_chat_retention_policies_v2_project
  ON project_chat_retention_policies_v2(project_id);

CREATE TABLE IF NOT EXISTS project_chat_cleanup_logs_v2 (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  policy_id TEXT NOT NULL DEFAULT '',
  action_type TEXT NOT NULL DEFAULT 'archived',
  affected_message_count INTEGER NOT NULL DEFAULT 0,
  executed_by TEXT NOT NULL DEFAULT 'system',
  details_json TEXT NOT NULL DEFAULT '{}',
  executed_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_chat_cleanup_logs_v2_project
  ON project_chat_cleanup_logs_v2(project_id, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_chat_cleanup_logs_v2_action
  ON project_chat_cleanup_logs_v2(action_type, executed_at DESC);
