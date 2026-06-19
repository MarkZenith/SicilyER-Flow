-- Prediction procedure and dbt pipeline task with ML inference
-- Co-authored with CoCo
CREATE OR REPLACE PROCEDURE SICILY_ER_DB.SILVER.GENERATE_PREDICTIONS()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.9'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-ml-python')
HANDLER = 'main'
AS
$$
from snowflake.ml.registry import Registry
from snowflake.snowpark import functions as F

def main(session):
    # 1. RECUPERA IL MODELLO: Carica l'ultima versione dal Model Registry
    reg = Registry(session=session, database_name="SICILY_ER_DB", schema_name="SILVER")
    model = reg.get_model("MODELLO_ATTESA_ER")
    
    # 2. TROVA I PAZIENTI: Prendi solo chi è attualmente in pronto soccorso
    df_attesa = session.table("SICILY_ER_DB.SILVER.SILVER_ADMISSIONS").filter(F.col("STATUS") == 'In attesa')
    
    # 3. ESEGUI PREVISIONE E SALVA NEL GOLD
    if df_attesa.count() > 0:
        predictions = model.run(df_attesa, function_name="predict")
        predictions.write.mode("overwrite").save_as_table("SICILY_ER_DB.GOLD.PREDICTIONS")
        return "Tabella GOLD.PREDICTIONS aggiornata con i nuovi tempi di attesa!"
    else:
        return "Nessun paziente in attesa al momento."
$$;

CALL SICILY_ER_DB.SILVER.GENERATE_PREDICTIONS();