CREATE VIEW vw_alert_summary AS
SELECT
    uf.report_year,
    uf.report_month,
    uf.report_fortnight,
    uf.source_system,
    uf.fiu_alert_type,
    fa.*
FROM fiu_alerts fa
JOIN uploaded_files uf
ON fa.file_id = uf.file_id;