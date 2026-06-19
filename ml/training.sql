-- Stored procedure to train and register XGBoost wait-time model
-- Co-authored with CoCo
CREATE OR REPLACE PROCEDURE SICILY_ER_DB.SILVER.TRAIN_WAIT_TIME_MODEL_PRO()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-ml-python', 'xgboost', 'scikit-learn')
HANDLER = 'main'
AS
$$
from snowflake.ml.modeling.xgboost import XGBRegressor
from snowflake.ml.modeling.pipeline import Pipeline
from snowflake.ml.modeling.preprocessing import StandardScaler
from snowflake.ml.registry import Registry
from snowflake.snowpark import functions as F

def main(session):
    # 1. LETTURA DATI STORICI
    df = session.table("SICILY_ER_DB.SILVER.SILVER_ADMISSIONS").filter(F.col("STATUS") == 'Dimesso')
    
    # 2. FEATURE ENGINEERING
    df = df.with_column("CODICE_TRIAGE_NUM", 
        F.decode(
            F.col("CODICE_TRIAGE"), 
            F.lit("Rosso"), F.lit(1), 
            F.lit("Arancione"), F.lit(2), 
            F.lit("Giallo"), F.lit(3), 
            F.lit("Verde"), F.lit(4), 
            F.lit("Bianco"), F.lit(5), 
            F.lit(3) # Valore di default (Corretto per Python!)
        )
    )
    
    df = df.with_column("SESSO_M", F.when(F.col("SESSO") == "M", F.lit(1)).otherwise(F.lit(0)))
    
    FEATURES = ["CODICE_TRIAGE_NUM", "ETA_PAZIENTE", "SESSO_M", "ORA_ARRIVO"]
    TARGET = "ATTESA_STIMATA_MINUTI"
    
    # 3. ADDESTRAMENTO
    pipeline = Pipeline(steps=[
        ("scaler", StandardScaler(input_cols=FEATURES, output_cols=[f"{c}_S" for c in FEATURES])),
        ("model", XGBRegressor(input_cols=[f"{c}_S" for c in FEATURES], label_cols=[TARGET], output_cols=["PRED"]))
    ])
    pipeline.fit(df)
    
    # 4. VALUTAZIONE
    preds = pipeline.predict(df)
    mape = preds.select(F.avg(F.abs(F.col(TARGET) - F.col("PRED")) / F.col(TARGET)).alias("MAPE")).collect()[0]["MAPE"]
    accuracy_percent = (1 - mape) * 100
    
    # 5. SALVATAGGIO
    reg = Registry(session=session, database_name="SICILY_ER_DB", schema_name="SILVER")
    model_version = reg.log_model(
        pipeline, 
        model_name="MODELLO_ATTESA_ER", 
        comment=f"Accuratezza Modello: {accuracy_percent:.2f}%"
    )
    
    return f"Successo! Modello v{model_version.version_name} addestrato con accuratezza: {accuracy_percent:.2f}%"
$$;

CALL SICILY_ER_DB.SILVER.TRAIN_WAIT_TIME_MODEL_PRO();