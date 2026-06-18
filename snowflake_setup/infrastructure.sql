
-- 1. Creazione del Motore di Calcolo (Virtual Warehouse)
-- Usiamo XSMALL per minimizzare i costi (livello gratuito)
CREATE WAREHOUSE IF NOT EXISTS SICILY_ER_WH
WITH WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 60
AUTO_RESUME = TRUE
INITIALLY_SUSPENDED = TRUE;

-- 2. Creazione del Database Principale
CREATE DATABASE IF NOT EXISTS SICILY_ER_DB;
USE DATABASE SICILY_ER_DB;

-- 3. Creazione degli Schemi (Architettura a Medaglione)
CREATE SCHEMA IF NOT EXISTS BRONZE; -- Dati grezzi JSON
CREATE SCHEMA IF NOT EXISTS SILVER; -- Dati puliti e tipizzati
CREATE SCHEMA IF NOT EXISTS GOLD;   -- Dati aggregati per Machine Learning/BI

-- 4. Creazione del File Format per leggere i JSON
USE SCHEMA BRONZE;
CREATE OR REPLACE FILE_FORMAT json_format
  TYPE = 'JSON'
  STRIP_OUTER_ARRAY = TRUE;

-- 5. Creazione dello Stage 
CREATE OR REPLACE STAGE s3_raw_stage
  URL = 's3://INSERISCI_NOME_DEL_TUO_BUCKET/raw_admissions/'
  CREDENTIALS = (AWS_KEY_ID = 'INSERISCI_QUI_LA_CHIAVE' AWS_SECRET_KEY = 'INSERISCI_QUI_IL_SECRET')
  FILE_FORMAT = json_format;