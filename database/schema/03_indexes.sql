CREATE EXTENSION IF NOT EXISTS pg_trgm;


CREATE INDEX IF NOT EXISTS idx_uploaded_file_search
ON uploaded_files
(
    report_year,
    report_month,
    report_fortnight,
    source_system,
    fiu_alert_type
);


CREATE INDEX IF NOT EXISTS idx_alert_pan
ON fiu_alerts(alert_pan);

CREATE INDEX IF NOT EXISTS idx_source_pan
ON fiu_alerts(source_pan);

CREATE INDEX IF NOT EXISTS idx_target_pan
ON fiu_alerts(target_pan);

CREATE INDEX IF NOT EXISTS idx_isin
ON fiu_alerts(isin_code);

CREATE INDEX IF NOT EXISTS idx_transaction_indicator
ON fiu_alerts(transaction_indicator);

CREATE INDEX IF NOT EXISTS idx_alert_file
ON fiu_alerts(file_id);

CREATE INDEX IF NOT EXISTS idx_alert_name
ON fiu_alerts(alert_name);

CREATE INDEX IF NOT EXISTS idx_alert_client
ON fiu_alerts(alert_client_id);

CREATE INDEX IF NOT EXISTS idx_transaction_type
ON fiu_alerts(transaction_type);

CREATE INDEX IF NOT EXISTS idx_source_dp
ON fiu_alerts(source_dp_id);

CREATE INDEX IF NOT EXISTS idx_source_client
ON fiu_alerts(source_client_id);

CREATE INDEX IF NOT EXISTS idx_target_dp
ON fiu_alerts(target_dp_id);

CREATE INDEX IF NOT EXISTS idx_target_client
ON fiu_alerts(target_client_id);


-- Partial text-search indexes

CREATE INDEX IF NOT EXISTS idx_source_name_trgm
ON fiu_alerts
USING gin (source_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_target_name_trgm
ON fiu_alerts
USING gin (target_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_isin_name_trgm
ON fiu_alerts
USING gin (isin_name gin_trgm_ops);