CREATE WAREHOUSE IF NOT EXISTS SICILY_ER_WH
WITH WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 60
AUTO_RESUME = TRUE
INITIALLY_SUSPENDED = TRUE;

-- 2. Creazione del Database Principale e degli Schemi (Medallion Architecture)
CREATE DATABASE IF NOT EXISTS SICILY_ER_DB;
USE DATABASE SICILY_ER_DB;

CREATE SCHEMA IF NOT EXISTS BRONZE; 
CREATE SCHEMA IF NOT EXISTS SILVER; 
CREATE SCHEMA IF NOT EXISTS GOLD;   

USE SCHEMA BRONZE;

-- 3. Creazione della Storage Integration
-- Sostituisci l'ARN del ruolo con quello generato sulla console AWS IAM
CREATE OR REPLACE STORAGE INTEGRATION s3_secure_integration
  TYPE = 'EXTERNAL_STAGE'
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/SicilyER-Snowflake-Role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://IL_TUO_BUCKET/raw-data/');

-- Esegui questo comando nello scratchpad di Snowflake
-- per recuperare l'AWS_IAM_USER_ARN e lo STORAGE_AWS_EXTERNAL_ID necessari per AWS.
-- DESCRIBE INTEGRATION s3_secure_integration;

-- 4. Creazione del File Format per l'estrazione dei JSON
CREATE OR REPLACE FILE_FORMAT json_format
    TYPE = JSON
    COMPRESSION = AUTO
    STRIP_OUTER_ARRAY = TRUE
    IGNORE_UTF8_ERRORS = TRUE;

-- 5. Creazione dello Stage
CREATE OR REPLACE STAGE s3_raw_stage
  URL = 's3://IL_TUO_BUCKET/raw-data/'
  STORAGE_INTEGRATION = s3_secure_integration
  FILE_FORMAT = json_format;