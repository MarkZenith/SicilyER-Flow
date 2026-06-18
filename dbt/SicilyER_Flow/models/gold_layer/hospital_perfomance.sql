{{ config(
    materialized='table'
) }}


-- 1. Quante persone ci sono fisicamente in reparto ORA
WITH pazienti_attuali AS (
    SELECT
        id_ospedale,
        COUNT(id_accesso) AS pazienti_in_reparto_ora,
        -- Contiamo quanti casi gravi sono attualmente in gestione
        COUNT(CASE WHEN codice_triage IN ('Rosso', 'Arancione') THEN 1 END) AS casi_critici_ora
    FROM {{ ref('silver_admissions') }}
    WHERE status != 'Dimesso'
    GROUP BY id_ospedale
),
-- 2. Estraiamo tutti i cambi di stato dalla zona grezza
storico_eventi AS (
    SELECT
        raw_data:id_accesso::VARCHAR AS id_accesso,
        raw_data:id_ospedale::VARCHAR AS id_ospedale,
        raw_data:nome_ospedale::VARCHAR AS nome_ospedale,
        raw_data:status::VARCHAR AS status,
        raw_data:timestamp_evento::TIMESTAMP AS timestamp_evento
    FROM {{ source('er_bronze', 'raw') }}
),
-- 3. Mettiamo in riga l'orologio di ogni paziente
tempi_pazienti AS (
    SELECT
        id_accesso,
        id_ospedale,
        nome_ospedale,
        -- Trovo l'orario esatto di ogni fase per il singolo paziente
        MIN(CASE WHEN status = 'In attesa' THEN timestamp_evento END) AS orario_arrivo,
        MIN(CASE WHEN status = 'In visita' THEN timestamp_evento END) AS orario_visita,
        MIN(CASE WHEN status = 'In osservazione' THEN timestamp_evento END) AS orario_osservazione,
        MIN(CASE WHEN status = 'Dimesso' THEN timestamp_evento END) AS orario_dimissione
    FROM storico_eventi
    GROUP BY id_accesso, id_ospedale, nome_ospedale
),

-- 4. CALCOLO DURATE REALI (Sottrazione tra i timestamp)
durata_fasi AS (
    SELECT
        id_ospedale,
        nome_ospedale,
        id_accesso,
        -- Tempo di attesa (da quando entra a quando va in visita, o dimesso se scappa via)
        TIMESTAMPDIFF(MINUTE, orario_arrivo, COALESCE(orario_visita, orario_dimissione)) AS minuti_attesa_reali,
        
        -- Tempo di visita (dalla visita all'osservazione, o dimissione)
        TIMESTAMPDIFF(MINUTE, orario_visita, COALESCE(orario_osservazione, orario_dimissione)) AS minuti_visita_reali
    FROM tempi_pazienti
    WHERE orario_arrivo IS NOT NULL
),
-- 5. AGGREGAZIONE FINALE (Medie per ogni ospedale)
performance_storica AS (
    SELECT
        id_ospedale,
        nome_ospedale,
        COUNT(id_accesso) AS totale_pazienti_gestiti,
        ROUND(AVG(minuti_attesa_reali), 0) AS tempo_medio_attesa_reale,
        ROUND(AVG(minuti_visita_reali), 0) AS tempo_medio_visita_reale
    FROM durata_fasi
    GROUP BY id_ospedale, nome_ospedale
)
-- 6. Unisce le performance con i pazienti in reparto ora
SELECT
    p.id_ospedale,
    p.nome_ospedale,
    COALESCE(a.pazienti_in_reparto_ora, 0) AS pazienti_in_reparto_ora,
    COALESCE(a.casi_critici_ora, 0) AS casi_critici_ora,
    p.totale_pazienti_gestiti,
    p.tempo_medio_attesa_reale,
    p.tempo_medio_visita_reale
FROM performance_storica p
LEFT JOIN pazienti_attuali a ON p.id_ospedale = a.id_ospedale
ORDER BY pazienti_in_reparto_ora DESC