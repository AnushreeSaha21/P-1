CREATE TABLE fiu_alerts (

    record_id BIGSERIAL PRIMARY KEY,

    file_id INTEGER NOT NULL
        REFERENCES uploaded_files(file_id)
        ON DELETE CASCADE,

    -------------------------------------------------------
    -- SOURCE DETAILS
    -------------------------------------------------------

    source_dp_id             VARCHAR(25),

    source_client_id         VARCHAR(30),

    source_name              VARCHAR(255),

    source_pan               VARCHAR(20),

    source_bank_name         VARCHAR(255),

    source_branch_name       VARCHAR(255),

    source_ifsc              VARCHAR(20),

    source_bank_account      VARCHAR(50),

    source_address           TEXT,

    source_city              VARCHAR(100),

    source_pincode           VARCHAR(15),

    -------------------------------------------------------
    -- TARGET DETAILS
    -------------------------------------------------------

    target_dp_id             VARCHAR(25),

    target_client_id         VARCHAR(30),

    target_name              VARCHAR(255),

    target_pan               VARCHAR(20),

    target_bank_name         VARCHAR(255),

    target_branch_name       VARCHAR(255),

    target_ifsc              VARCHAR(20),

    target_bank_account      VARCHAR(50),

    target_address           TEXT,

    target_city              VARCHAR(100),

    target_pincode           VARCHAR(15),

    -------------------------------------------------------
    -- ALERT ACCOUNT DETAILS
    -------------------------------------------------------

    alert_side               VARCHAR(10)
    CHECK (alert_side IN ('SOURCE', 'TARGET', 'UNKNOWN')),

    alert_client_id          VARCHAR(30),

    alert_name               VARCHAR(255),

    alert_pan                VARCHAR(20) NOT NULL,

    -------------------------------------------------------
    -- TRANSACTION DETAILS
    -------------------------------------------------------

    transaction_indicator    VARCHAR(2)
        CHECK (transaction_indicator IN ('DR','CR')),

    transaction_type         VARCHAR(100),

    market_type              VARCHAR(100),

    -------------------------------------------------------
    -- SECURITY DETAILS
    -------------------------------------------------------

    isin_code                VARCHAR(20) NOT NULL,

    isin_name                VARCHAR(500),

    quantity                 NUMERIC(20,4),

    isin_price               NUMERIC(20,4),

    valuation                NUMERIC(20,2),

    -------------------------------------------------------
    -- TOTALS
    -------------------------------------------------------

    market_total             NUMERIC(20,4),

    remat_total              NUMERIC(20,4),

    demat_total              NUMERIC(20,4),

    ca_total                 NUMERIC(20,4),

    ipo_total                NUMERIC(20,4),

    confis_total             NUMERIC(20,4),

    grand_total              NUMERIC(20,4),

    -------------------------------------------------------
    -- AUDIT
    -------------------------------------------------------

    inserted_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);