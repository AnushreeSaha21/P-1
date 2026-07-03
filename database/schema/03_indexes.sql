CREATE INDEX idx_uploaded_files_source
ON uploaded_files(source_system);

CREATE INDEX idx_uploaded_files_period
ON uploaded_files(report_year, report_month, report_fortnight);

CREATE INDEX idx_alert_pan
ON fiu_alerts(alert_pan);

CREATE INDEX idx_source_pan
ON fiu_alerts(source_pan);

CREATE INDEX idx_target_pan
ON fiu_alerts(target_pan);

CREATE INDEX idx_isin
ON fiu_alerts(isin_code);

CREATE INDEX idx_transaction_indicator
ON fiu_alerts(transaction_indicator);

CREATE INDEX idx_alert_file
ON fiu_alerts(file_id);

CREATE INDEX idx_alert_name
ON fiu_alerts(alert_name);

CREATE INDEX idx_alert_client
ON fiu_alerts(alert_client_id);

CREATE INDEX idx_transaction_type
ON fiu_alerts(transaction_type);