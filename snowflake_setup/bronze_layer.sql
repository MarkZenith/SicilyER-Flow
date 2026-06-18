USE DATABASE SICILY_ER_DB;
USE SCHEMA BRONZE;
USE WAREHOUSE SICILY_ER_WH;

-- 1. Creazione della tabella raw
CREATE OR REPLACE TABLE raw (
    raw_data VARIANT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Creazione dello Snowpipe 
CREATE OR REPLACE PIPE s3_raw_pipe
    AUTO_INGEST = TRUE
    AS
    COPY INTO raw (raw_data)
    FROM @s3_raw_stage
    FILE_FORMAT = (FORMAT_NAME = 'json_format');


-- 3. RECUPERO DELLA CODA SQS (Fondamentale per AWS)
-- Esegui questo comando per ottenere la stringa "notification_channel"
DESCRIBE PIPE s3_raw_pipe;