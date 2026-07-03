CREATE TABLE uploaded_files (

    file_id              SERIAL PRIMARY KEY,

    -- File Information
    file_name            VARCHAR(255) NOT NULL UNIQUE,
    original_file_name   VARCHAR(255),

    -- CDSL / NSDL
    source_system        VARCHAR(10) NOT NULL
        CHECK (source_system IN ('CDSL','NSDL')),

    -- FIU Alert Type (1-5)
    fiu_alert_type       SMALLINT NOT NULL
        CHECK (fiu_alert_type BETWEEN 1 AND 5),

    -- Reporting Period
    report_year          SMALLINT NOT NULL,
    report_month         SMALLINT NOT NULL
        CHECK (report_month BETWEEN 1 AND 12),

    report_fortnight     SMALLINT NOT NULL
        CHECK (report_fortnight IN (1,2)),

    fortnight_start      DATE NOT NULL,
    fortnight_end        DATE NOT NULL,

    -- Upload Information
    upload_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    total_records        INTEGER DEFAULT 0

);