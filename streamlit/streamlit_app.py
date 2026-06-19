
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.exceptions import SnowparkSQLException
import pandas as pd
import altair as alt

# ─── CONFIGURAZIONE PAGINA ──────────────────────────────────────────────────
st.set_page_config(page_title="Sicily ER - Attese Live", page_icon="🚑", layout="wide")
st.title("🚑 Pronto Soccorso Live: Previsione Attese")
st.markdown("Monitoraggio in tempo reale dei pazienti in attesa, basato su intelligenza artificiale.")

# ─── CONNESSIONE AI DATI ────────────────────────────────────────────────────
session = get_active_session()

# Leggiamo la tabella GOLD popolata dal tuo modello ML
@st.cache_data(ttl=60) # Aggiorna la cache ogni 60 secondi
def load_predictions():
    query = """
        SELECT 
            ID_PAZIENTE, 
            CODICE_TRIAGE, 
            ETA_PAZIENTE, 
            ORA_ARRIVO, 
            ROUND(PRED, 0) AS ATTESA_PREVISTA_MINUTI
        FROM SICILY_ER_DB.GOLD.PREDICTIONS
        ORDER BY CODICE_TRIAGE_NUM ASC, ATTESA_PREVISTA_MINUTI DESC
    """
    try:
        return session.sql(query).to_pandas()
    except SnowparkSQLException:
        return pd.DataFrame()

# Caricamento del dataframe
df = load_predictions()

# ─── SEZIONE 1: METRICHE PRINCIPALI (KPI) ───────────────────────────────────
if df.empty:
    st.success("🎉 Nessun paziente in attesa al momento. Il Pronto Soccorso è vuoto!")
else:
    # Calcolo delle metriche veloci
    tot_pazienti = len(df)
    attesa_media = int(df["ATTESA_PREVISTA_MINUTI"].mean())
    attesa_max = int(df["ATTESA_PREVISTA_MINUTI"].max())

    col1, col2, col3 = st.columns(3)
    col1.metric("Pazienti in Attesa", tot_pazienti)
    col2.metric("Attesa Media Stimata", f"{attesa_media} min")
    col3.metric("Attesa Massima", f"{attesa_max} min", delta_color="inverse")

    st.divider()

    # ─── SEZIONE 2: GRAFICI E TABELLE ───────────────────────────────────────
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        st.subheader("Pazienti per Codice Triage")
        # Conta quanti pazienti ci sono per ogni colore di triage
        triage_counts = df["CODICE_TRIAGE"].value_counts().reset_index()
        triage_counts.columns = ["CODICE_TRIAGE", "NUMERO_PAZIENTI"]
        
        # Mappa colori personalizzata per i codici Triage
        color_scale = alt.Scale(
            domain=["Rosso", "Arancione", "Giallo", "Verde", "Bianco"],
            range=["#FF0000", "#FFA500", "#FFD700", "#008000", "#FFFFFF"]
        )
        
        chart = alt.Chart(triage_counts).mark_bar().encode(
            x=alt.X("CODICE_TRIAGE", sort=["Rosso", "Arancione", "Giallo", "Verde", "Bianco"]),
            y="NUMERO_PAZIENTI",
            color=alt.Color("CODICE_TRIAGE", scale=color_scale, legend=None)
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)

    with col_table:
        st.subheader("Dettaglio Pazienti (Ordine di Priorità)")
        # Mostra la tabella interattiva
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ATTESA_PREVISTA_MINUTI": st.column_config.ProgressColumn(
                    "Attesa Prevista (Min)",
                    format="%f",
                    min_value=0,
                    max_value=300, # Imposta a 300 minuti (5 ore) il massimo della barra
                )
            }
        )

# Tasto per aggiornamento manuale
if st.button("🔄 Aggiorna Dati Ora"):
    st.cache_data.clear()
    st.rerun()