CREATE TABLE IF NOT EXISTS intelligence_free_data_providers_v2 (
  id TEXT PRIMARY KEY,
  provider_code TEXT NOT NULL UNIQUE,
  provider_name TEXT NOT NULL,
  provider_type TEXT NOT NULL DEFAULT 'mixed',
  base_url TEXT NOT NULL DEFAULT '',
  auth_type TEXT NOT NULL DEFAULT 'none',
  api_key_env_name TEXT NOT NULL DEFAULT '',
  free_tier_limit_json TEXT NOT NULL DEFAULT '{}',
  rate_limit_per_minute INTEGER NOT NULL DEFAULT 0,
  rate_limit_per_day INTEGER NOT NULL DEFAULT 0,
  is_active INTEGER NOT NULL DEFAULT 1,
  priority_score INTEGER NOT NULL DEFAULT 50,
  terms_note TEXT NOT NULL DEFAULT '',
  config_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS intelligence_provider_rate_limit_state_v2 (
  id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL,
  window_type TEXT NOT NULL DEFAULT 'minute',
  window_start_at INTEGER NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 0,
  last_request_at INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_rate_limit_unique
  ON intelligence_provider_rate_limit_state_v2(provider_id, window_type, window_start_at);

CREATE TABLE IF NOT EXISTS intelligence_market_indices_v2 (
  id TEXT PRIMARY KEY,
  country_code TEXT NOT NULL,
  region_code TEXT NOT NULL,
  market_name_en TEXT NOT NULL DEFAULT '',
  market_name_zh TEXT NOT NULL DEFAULT '',
  index_code TEXT NOT NULL UNIQUE,
  index_symbol TEXT NOT NULL,
  index_name_en TEXT NOT NULL,
  index_name_zh TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT '',
  exchange_timezone TEXT NOT NULL DEFAULT '',
  display_order INTEGER NOT NULL DEFAULT 100,
  is_active INTEGER NOT NULL DEFAULT 1,
  primary_provider_id TEXT NOT NULL DEFAULT '',
  fallback_provider_ids_json TEXT NOT NULL DEFAULT '[]',
  provider_symbol_map_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_market_indices_region
  ON intelligence_market_indices_v2(region_code, country_code, display_order);

CREATE TABLE IF NOT EXISTS intelligence_market_index_latest_snapshots_v2 (
  id TEXT PRIMARY KEY,
  index_id TEXT NOT NULL UNIQUE,
  provider_id TEXT NOT NULL DEFAULT '',
  snapshot_time INTEGER NOT NULL,
  current_value REAL NOT NULL DEFAULT 0,
  previous_close REAL NOT NULL DEFAULT 0,
  open_value REAL NOT NULL DEFAULT 0,
  high_value REAL NOT NULL DEFAULT 0,
  low_value REAL NOT NULL DEFAULT 0,
  change_value REAL NOT NULL DEFAULT 0,
  change_percent REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  market_status TEXT NOT NULL DEFAULT 'unknown',
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS intelligence_market_index_snapshots_history_v2 (
  id TEXT PRIMARY KEY,
  index_id TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  snapshot_time INTEGER NOT NULL,
  current_value REAL NOT NULL DEFAULT 0,
  previous_close REAL NOT NULL DEFAULT 0,
  open_value REAL NOT NULL DEFAULT 0,
  high_value REAL NOT NULL DEFAULT 0,
  low_value REAL NOT NULL DEFAULT 0,
  change_value REAL NOT NULL DEFAULT 0,
  change_percent REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  market_status TEXT NOT NULL DEFAULT 'unknown',
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_market_hist_index_time
  ON intelligence_market_index_snapshots_history_v2(index_id, snapshot_time DESC);

CREATE TABLE IF NOT EXISTS intelligence_market_index_timeseries_v2 (
  id TEXT PRIMARY KEY,
  index_id TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  interval_type TEXT NOT NULL DEFAULT '1h',
  point_time INTEGER NOT NULL,
  open_value REAL NOT NULL DEFAULT 0,
  high_value REAL NOT NULL DEFAULT 0,
  low_value REAL NOT NULL DEFAULT 0,
  close_value REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_market_timeseries_unique
  ON intelligence_market_index_timeseries_v2(index_id, interval_type, point_time);

CREATE INDEX IF NOT EXISTS idx_intel_market_timeseries_index_interval
  ON intelligence_market_index_timeseries_v2(index_id, interval_type, point_time DESC);

CREATE TABLE IF NOT EXISTS intelligence_news_sources_v2 (
  id TEXT PRIMARY KEY,
  source_code TEXT NOT NULL UNIQUE,
  source_name_en TEXT NOT NULL,
  source_name_zh TEXT NOT NULL,
  source_type TEXT NOT NULL DEFAULT 'rss',
  provider_id TEXT NOT NULL DEFAULT '',
  source_country TEXT NOT NULL DEFAULT '',
  source_language TEXT NOT NULL DEFAULT '',
  homepage_url TEXT NOT NULL DEFAULT '',
  feed_url TEXT NOT NULL DEFAULT '',
  default_category TEXT NOT NULL DEFAULT 'general',
  priority_score INTEGER NOT NULL DEFAULT 50,
  is_non_china_media INTEGER NOT NULL DEFAULT 1,
  is_active INTEGER NOT NULL DEFAULT 1,
  copyright_policy TEXT NOT NULL DEFAULT 'metadata_summary_link_only',
  config_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS intelligence_news_source_feeds_v2 (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'general',
  feed_name TEXT NOT NULL DEFAULT '',
  feed_url TEXT NOT NULL,
  language_code TEXT NOT NULL DEFAULT '',
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_news_feeds_source
  ON intelligence_news_source_feeds_v2(source_id, is_active);

CREATE TABLE IF NOT EXISTS intelligence_news_articles_v2 (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL DEFAULT '',
  provider_id TEXT NOT NULL DEFAULT '',
  external_id TEXT NOT NULL DEFAULT '',
  original_url TEXT NOT NULL UNIQUE,
  canonical_url TEXT NOT NULL DEFAULT '',
  title_original TEXT NOT NULL,
  title_en TEXT NOT NULL DEFAULT '',
  title_zh TEXT NOT NULL DEFAULT '',
  original_language TEXT NOT NULL DEFAULT '',
  published_at INTEGER NOT NULL DEFAULT 0,
  fetched_at INTEGER NOT NULL,
  raw_excerpt TEXT NOT NULL DEFAULT '',
  raw_content TEXT NOT NULL DEFAULT '',
  category_primary TEXT NOT NULL DEFAULT 'general',
  tags_json TEXT NOT NULL DEFAULT '[]',
  entities_json TEXT NOT NULL DEFAULT '[]',
  country_tags_json TEXT NOT NULL DEFAULT '[]',
  region_tags_json TEXT NOT NULL DEFAULT '[]',
  dedup_key TEXT NOT NULL DEFAULT '',
  cluster_key TEXT NOT NULL DEFAULT '',
  importance_score REAL NOT NULL DEFAULT 0,
  relevance_score REAL NOT NULL DEFAULT 0,
  source_priority_score INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'fetched',
  rejection_reason TEXT NOT NULL DEFAULT '',
  copyright_mode TEXT NOT NULL DEFAULT 'metadata_summary_link_only',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_news_articles_published
  ON intelligence_news_articles_v2(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_news_articles_category
  ON intelligence_news_articles_v2(category_primary, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_news_articles_status
  ON intelligence_news_articles_v2(status, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_news_articles_cluster
  ON intelligence_news_articles_v2(cluster_key, published_at DESC);

CREATE TABLE IF NOT EXISTS intelligence_news_article_clusters_v2 (
  id TEXT PRIMARY KEY,
  cluster_key TEXT NOT NULL UNIQUE,
  representative_article_id TEXT NOT NULL DEFAULT '',
  normalized_title TEXT NOT NULL DEFAULT '',
  topic_signature TEXT NOT NULL DEFAULT '',
  article_count INTEGER NOT NULL DEFAULT 1,
  source_count INTEGER NOT NULL DEFAULT 1,
  first_published_at INTEGER NOT NULL DEFAULT 0,
  latest_published_at INTEGER NOT NULL DEFAULT 0,
  category_primary TEXT NOT NULL DEFAULT 'general',
  tags_json TEXT NOT NULL DEFAULT '[]',
  cluster_importance_score REAL NOT NULL DEFAULT 0,
  cluster_relevance_score REAL NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS intelligence_news_article_summaries_v2 (
  id TEXT PRIMARY KEY,
  article_id TEXT NOT NULL,
  language_code TEXT NOT NULL,
  summary_title TEXT NOT NULL DEFAULT '',
  summary_content TEXT NOT NULL DEFAULT '',
  summary_length INTEGER NOT NULL DEFAULT 0,
  summarizer_type TEXT NOT NULL DEFAULT 'rule_based',
  summarizer_provider TEXT NOT NULL DEFAULT '',
  summarizer_metadata_json TEXT NOT NULL DEFAULT '{}',
  quality_score REAL NOT NULL DEFAULT 0,
  generated_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_news_summaries_unique
  ON intelligence_news_article_summaries_v2(article_id, language_code);

CREATE TABLE IF NOT EXISTS intelligence_news_daily_digest_items_v2 (
  id TEXT PRIMARY KEY,
  digest_window_start INTEGER NOT NULL,
  digest_window_end INTEGER NOT NULL,
  digest_date TEXT NOT NULL,
  language_code TEXT NOT NULL,
  article_id TEXT NOT NULL,
  summary_id TEXT NOT NULL DEFAULT '',
  ranking_order INTEGER NOT NULL,
  category_primary TEXT NOT NULL DEFAULT 'general',
  importance_score REAL NOT NULL DEFAULT 0,
  relevance_score REAL NOT NULL DEFAULT 0,
  is_top30 INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_digest_unique_rank
  ON intelligence_news_daily_digest_items_v2(digest_date, language_code, ranking_order);
CREATE INDEX IF NOT EXISTS idx_intel_digest_date_lang
  ON intelligence_news_daily_digest_items_v2(digest_date, language_code, ranking_order);

CREATE TABLE IF NOT EXISTS intelligence_job_runs_v2 (
  id TEXT PRIMARY KEY,
  job_name TEXT NOT NULL,
  job_type TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'queued',
  started_at INTEGER NOT NULL DEFAULT 0,
  completed_at INTEGER NOT NULL DEFAULT 0,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  fetched_count INTEGER NOT NULL DEFAULT 0,
  processed_count INTEGER NOT NULL DEFAULT 0,
  inserted_count INTEGER NOT NULL DEFAULT 0,
  updated_count INTEGER NOT NULL DEFAULT 0,
  skipped_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT NOT NULL DEFAULT '',
  error_stack TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_job_runs_type_time
  ON intelligence_job_runs_v2(job_type, created_at DESC);

CREATE TABLE IF NOT EXISTS intelligence_provider_errors_v2 (
  id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL DEFAULT '',
  error_type TEXT NOT NULL DEFAULT '',
  error_message TEXT NOT NULL DEFAULT '',
  http_status INTEGER NOT NULL DEFAULT 0,
  request_url TEXT NOT NULL DEFAULT '',
  occurred_at INTEGER NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_intel_provider_errors_time
  ON intelligence_provider_errors_v2(provider_id, occurred_at DESC);
