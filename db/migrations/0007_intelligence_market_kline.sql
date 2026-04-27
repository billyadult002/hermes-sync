CREATE TABLE IF NOT EXISTS intelligence_market_instruments_v2 (
  id TEXT PRIMARY KEY,
  instrument_type TEXT NOT NULL DEFAULT 'stock',
  symbol TEXT NOT NULL,
  name_en TEXT NOT NULL DEFAULT '',
  name_zh TEXT NOT NULL DEFAULT '',
  country_code TEXT NOT NULL DEFAULT '',
  region_code TEXT NOT NULL DEFAULT '',
  exchange_code TEXT NOT NULL DEFAULT '',
  exchange_name_en TEXT NOT NULL DEFAULT '',
  exchange_name_zh TEXT NOT NULL DEFAULT '',
  currency TEXT NOT NULL DEFAULT '',
  timezone TEXT NOT NULL DEFAULT '',
  is_active INTEGER NOT NULL DEFAULT 1,
  primary_provider_id TEXT NOT NULL DEFAULT '',
  fallback_provider_ids_json TEXT NOT NULL DEFAULT '[]',
  provider_symbol_map_json TEXT NOT NULL DEFAULT '{}',
  search_keywords TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_instruments_type_symbol_unique
  ON intelligence_market_instruments_v2(instrument_type, symbol);
CREATE INDEX IF NOT EXISTS idx_intel_instruments_active_type_symbol
  ON intelligence_market_instruments_v2(is_active, instrument_type, symbol);
CREATE INDEX IF NOT EXISTS idx_intel_instruments_name_en
  ON intelligence_market_instruments_v2(name_en);
CREATE INDEX IF NOT EXISTS idx_intel_instruments_name_zh
  ON intelligence_market_instruments_v2(name_zh);
CREATE INDEX IF NOT EXISTS idx_intel_instruments_exchange
  ON intelligence_market_instruments_v2(exchange_code, country_code);

CREATE TABLE IF NOT EXISTS intelligence_instrument_latest_quotes_v2 (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL UNIQUE,
  provider_id TEXT NOT NULL DEFAULT '',
  quote_time INTEGER NOT NULL,
  last_price REAL NOT NULL DEFAULT 0,
  previous_close REAL NOT NULL DEFAULT 0,
  open_price REAL NOT NULL DEFAULT 0,
  high_price REAL NOT NULL DEFAULT 0,
  low_price REAL NOT NULL DEFAULT 0,
  change_value REAL NOT NULL DEFAULT 0,
  change_percent REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  bid_price REAL NOT NULL DEFAULT 0,
  ask_price REAL NOT NULL DEFAULT 0,
  delayed_flag INTEGER NOT NULL DEFAULT 1,
  market_status TEXT NOT NULL DEFAULT 'unknown',
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_latest_quotes_time
  ON intelligence_instrument_latest_quotes_v2(quote_time DESC);

CREATE TABLE IF NOT EXISTS intelligence_instrument_quote_snapshots_v2 (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  quote_time INTEGER NOT NULL,
  last_price REAL NOT NULL DEFAULT 0,
  previous_close REAL NOT NULL DEFAULT 0,
  open_price REAL NOT NULL DEFAULT 0,
  high_price REAL NOT NULL DEFAULT 0,
  low_price REAL NOT NULL DEFAULT 0,
  change_value REAL NOT NULL DEFAULT 0,
  change_percent REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  bid_price REAL NOT NULL DEFAULT 0,
  ask_price REAL NOT NULL DEFAULT 0,
  delayed_flag INTEGER NOT NULL DEFAULT 1,
  market_status TEXT NOT NULL DEFAULT 'unknown',
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intel_quote_snapshots_instrument_time
  ON intelligence_instrument_quote_snapshots_v2(instrument_id, quote_time DESC);

CREATE TABLE IF NOT EXISTS intelligence_instrument_ohlcv_timeseries_v2 (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  interval_type TEXT NOT NULL DEFAULT '1d',
  point_time INTEGER NOT NULL,
  adjusted_flag INTEGER NOT NULL DEFAULT 1,
  open_price REAL NOT NULL DEFAULT 0,
  high_price REAL NOT NULL DEFAULT 0,
  low_price REAL NOT NULL DEFAULT 0,
  close_price REAL NOT NULL DEFAULT 0,
  adjusted_close REAL NOT NULL DEFAULT 0,
  volume REAL NOT NULL DEFAULT 0,
  turnover_amount REAL NOT NULL DEFAULT 0,
  dividend_amount REAL NOT NULL DEFAULT 0,
  split_coefficient REAL NOT NULL DEFAULT 0,
  data_quality TEXT NOT NULL DEFAULT 'normal',
  source_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_ohlcv_unique
  ON intelligence_instrument_ohlcv_timeseries_v2(instrument_id, interval_type, point_time, adjusted_flag);
CREATE INDEX IF NOT EXISTS idx_intel_ohlcv_query
  ON intelligence_instrument_ohlcv_timeseries_v2(instrument_id, interval_type, adjusted_flag, point_time DESC);

CREATE TABLE IF NOT EXISTS intelligence_instrument_corporate_actions_v2 (
  id TEXT PRIMARY KEY,
  instrument_id TEXT NOT NULL,
  provider_id TEXT NOT NULL DEFAULT '',
  action_type TEXT NOT NULL DEFAULT '',
  action_date INTEGER NOT NULL DEFAULT 0,
  ex_date INTEGER NOT NULL DEFAULT 0,
  record_date INTEGER NOT NULL DEFAULT 0,
  pay_date INTEGER NOT NULL DEFAULT 0,
  dividend_amount REAL NOT NULL DEFAULT 0,
  split_from REAL NOT NULL DEFAULT 0,
  split_to REAL NOT NULL DEFAULT 0,
  split_coefficient REAL NOT NULL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT '',
  reference TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_corp_actions_unique
  ON intelligence_instrument_corporate_actions_v2(instrument_id, action_type, action_date, reference);
CREATE INDEX IF NOT EXISTS idx_intel_corp_actions_query
  ON intelligence_instrument_corporate_actions_v2(instrument_id, action_date DESC);

CREATE TABLE IF NOT EXISTS intelligence_instrument_watchlists_v2 (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  instrument_id TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_intel_watchlist_unique
  ON intelligence_instrument_watchlists_v2(user_id, instrument_id);
CREATE INDEX IF NOT EXISTS idx_intel_watchlist_user
  ON intelligence_instrument_watchlists_v2(user_id, created_at DESC);
