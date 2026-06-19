{{ config(
    materialized='table'
) }}

WITH raw_data AS (
    SELECT * FROM {{ source('er_bronze', 'raw') }}
)

SELECT
    raw_data:id_accesso::VARCHAR AS id_accesso,
    raw_data:timestamp_arrivo::TIMESTAMP AS timestamp_arrivo,
    
    raw_data:timestamp_evento::TIMESTAMP AS timestamp_evento,
    
    raw_data:id_ospedale::VARCHAR AS id_ospedale,
    raw_data:nome_ospedale::VARCHAR AS nome_ospedale,
    raw_data:codice_triage::VARCHAR AS codice_triage,
    raw_data:eta_paziente::INTEGER AS eta_paziente,
    raw_data:sesso::VARCHAR AS sesso,
    raw_data:sintomo_principale::VARCHAR AS sintomo_principale,
    raw_data:status::VARCHAR AS status,
    raw_data:ora_arrivo::INTEGER AS ora_arrivo,
    raw_data:giorno_settimana::INTEGER AS giorno_settimana,
    raw_data:mese::INTEGER AS mese,
    raw_data:attesa_stimata_minuti::INTEGER AS attesa_stimata_minuti
FROM raw_data

--  partiziona i dati per paziente e tiene solo l'evento più recente
WHERE timestamp_evento <= CURRENT_TIMESTAMP()
QUALIFY ROW_NUMBER() OVER (PARTITION BY id_accesso ORDER BY timestamp_evento DESC) = 1