USE DATABASE SICILY_ER_DB;
USE SCHEMA SILVER;

-- 1. Creazione Task
CREATE OR REPLACE TASK run_sicily_dbt_pipeline
    WAREHOUSE = SICILY_ER_WH
    SCHEDULE = '10 MINUTE'
AS
    -- INSERISCI QUI IL NOME DEL TUO PROGETTO DBT SU SNOWFLAKE
    EXECUTE DBT PROJECT nome_tuo_progetto_dbt;

-- 2. Attivazione task
ALTER TASK run_sicily_dbt_pipeline RESUME;

-- Comandi utili per il monitoraggio futuro:
-- Per spegnerlo: ALTER TASK run_sicily_dbt_pipeline SUSPEND;
-- Per vedere lo storico: 
-- SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(TASK_NAME=>'RUN_SICILY_DBT_PIPELINE'));