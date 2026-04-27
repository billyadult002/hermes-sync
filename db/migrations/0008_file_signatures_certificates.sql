ALTER TABLE file_workflows_v2 ADD COLUMN title TEXT NOT NULL DEFAULT '';
ALTER TABLE file_workflows_v2 ADD COLUMN routing_mode TEXT NOT NULL DEFAULT 'sequential';
ALTER TABLE file_workflows_v2 ADD COLUMN due_at INTEGER NOT NULL DEFAULT 0;
ALTER TABLE file_workflows_v2 ADD COLUMN instructions TEXT NOT NULL DEFAULT '';
ALTER TABLE file_workflows_v2 ADD COLUMN signature_method TEXT NOT NULL DEFAULT 'platform';
ALTER TABLE file_workflows_v2 ADD COLUMN signature_placement TEXT NOT NULL DEFAULT '';
ALTER TABLE file_workflows_v2 ADD COLUMN lock_after_sign INTEGER NOT NULL DEFAULT 1;
ALTER TABLE file_workflows_v2 ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}';

CREATE TABLE IF NOT EXISTS file_signer_certificates_v2 (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  subject_name TEXT NOT NULL DEFAULT '',
  issuer_name TEXT NOT NULL DEFAULT 'Hermes Internal Signing Authority',
  public_key_fingerprint TEXT NOT NULL,
  secret_cipher TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  valid_from INTEGER NOT NULL,
  valid_to INTEGER NOT NULL,
  created_by TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  revoked_at INTEGER NOT NULL DEFAULT 0,
  revoked_by TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_file_signer_certificates_user ON file_signer_certificates_v2(user_id, status);
CREATE INDEX IF NOT EXISTS idx_file_signer_certificates_status ON file_signer_certificates_v2(status);

CREATE TABLE IF NOT EXISTS file_signature_records_v2 (
  id TEXT PRIMARY KEY,
  file_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  signer_id TEXT NOT NULL,
  certificate_id TEXT NOT NULL DEFAULT '',
  signature_method TEXT NOT NULL DEFAULT 'platform',
  hash_algorithm TEXT NOT NULL DEFAULT 'SHA-256',
  signed_hash TEXT NOT NULL,
  signature_algorithm TEXT NOT NULL DEFAULT 'HMAC-SHA256',
  signature_value TEXT NOT NULL,
  signed_at INTEGER NOT NULL,
  verify_status TEXT NOT NULL DEFAULT 'valid',
  verified_at INTEGER NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_file_signature_records_file ON file_signature_records_v2(file_id);
CREATE INDEX IF NOT EXISTS idx_file_signature_records_version ON file_signature_records_v2(version_id);
CREATE INDEX IF NOT EXISTS idx_file_signature_records_signer ON file_signature_records_v2(signer_id);
