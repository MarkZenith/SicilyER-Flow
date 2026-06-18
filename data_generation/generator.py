"""
SicilyER-Flow: Mock Data Generator
Simula accessi realistici ai Pronto Soccorso (ER) della Regione Siciliana.
Genera payload JSON includendo logiche di business come picchi orari, 
distribuzione reale dei codici di triage e pesi demografici.
"""

import json
import random
import uuid
from datetime import datetime, timezone
from faker import Faker

# Inizializza Faker per dati localizzati in italiano
fake = Faker('it_IT')

# Dizionario Ospedali: i "pesi" riflettono i volumi reali di accesso delle province siciliane
OSPEDALI = [
    # --- PALERMO E PROVINCIA (Peso totale: 0.26) ---
    {"id": "OSP_CIVICO_PA", "nome": "Civico - Palermo", "peso": 0.08},
    {"id": "OSP_VILLA_SOFIA_PA", "nome": "Villa Sofia Cervello - Palermo", "peso": 0.07},
    {"id": "OSP_POLICLINICO_PA", "nome": "Policlinico Giaccone - Palermo", "peso": 0.05},
    {"id": "OSP_BUCCHERI_PA", "nome": "Buccheri La Ferla - Palermo", "peso": 0.03},
    {"id": "OSP_INGRASSIA_PA", "nome": "Ingrassia - Palermo", "peso": 0.01},
    {"id": "OSP_TERMINI_PA", "nome": "Cimino - Termini Imerese (PA)", "peso": 0.01},
    {"id": "OSP_PARTINICO_PA", "nome": "Civico - Partinico (PA)", "peso": 0.01},

    # --- CATANIA E PROVINCIA (Peso totale: 0.24) ---
    {"id": "OSP_GARIBALDI_CT", "nome": "Garibaldi - Catania", "peso": 0.08},
    {"id": "OSP_CANNIZZARO_CT", "nome": "Cannizzaro - Catania", "peso": 0.07},
    {"id": "OSP_POLICLINICO_CT", "nome": "Policlinico San Marco - Catania", "peso": 0.06},
    {"id": "OSP_ACIREALE_CT", "nome": "Santa Marta - Acireale (CT)", "peso": 0.02},
    {"id": "OSP_CALTAGIRONE_CT", "nome": "Gravina - Caltagirone (CT)", "peso": 0.01},

    # --- MESSINA E PROVINCIA (Peso totale: 0.13) ---
    {"id": "OSP_POLICLINICO_ME", "nome": "Policlinico Martino - Messina", "peso": 0.04},
    {"id": "OSP_PAPARDO_ME", "nome": "Papardo - Messina", "peso": 0.04},
    {"id": "OSP_MILAZZO_ME", "nome": "Fogliani - Milazzo (ME)", "peso": 0.02},
    {"id": "OSP_TAORMINA_ME", "nome": "San Vincenzo - Taormina (ME)", "peso": 0.02},
    {"id": "OSP_PATTI_ME", "nome": "Barone Romeo - Patti (ME)", "peso": 0.01},

    # --- TRAPANI E PROVINCIA (Peso totale: 0.08) ---
    {"id": "OSP_SANT_ANTONIO_TP", "nome": "Sant'Antonio Abate - Trapani", "peso": 0.03},
    {"id": "OSP_MARSALA_TP", "nome": "Paolo Borsellino - Marsala (TP)", "peso": 0.02},
    {"id": "OSP_MAZARA_TP", "nome": "Abele Ajello - Mazara del Vallo (TP)", "peso": 0.02},
    {"id": "OSP_CASTELVETRANO_TP", "nome": "Vittorio Emanuele II - Castelvetrano (TP)", "peso": 0.01},

    # --- SIRACUSA E PROVINCIA (Peso totale: 0.08) ---
    {"id": "OSP_UMBERTO_SR", "nome": "Umberto I - Siracusa", "peso": 0.04},
    {"id": "OSP_AVOLA_SR", "nome": "Di Maria - Avola (SR)", "peso": 0.02},
    {"id": "OSP_LENTINI_SR", "nome": "Ospedale Civile - Lentini (SR)", "peso": 0.02},

    # --- AGRIGENTO E PROVINCIA (Peso totale: 0.07) ---
    {"id": "OSP_GIOVANNI_AG", "nome": "San Giovanni di Dio - Agrigento", "peso": 0.03},
    {"id": "OSP_SCIACCA_AG", "nome": "Giovanni Paolo II - Sciacca (AG)", "peso": 0.02},
    {"id": "OSP_CANICATTI_AG", "nome": "Barone Lombardo - Canicattì (AG)", "peso": 0.02},

    # --- RAGUSA E PROVINCIA (Peso totale: 0.06) ---
    {"id": "OSP_GIOVANNI_RG", "nome": "Giovanni Paolo II - Ragusa", "peso": 0.03},
    {"id": "OSP_VITTORIA_RG", "nome": "Guzzardi - Vittoria (RG)", "peso": 0.02},
    {"id": "OSP_MODICA_RG", "nome": "Maggiore - Modica (RG)", "peso": 0.01},

    # --- CALTANISSETTA E PROVINCIA (Peso totale: 0.05) ---
    {"id": "OSP_SANT_ELIA_CL", "nome": "Sant'Elia - Caltanissetta", "peso": 0.03},
    {"id": "OSP_GELA_CL", "nome": "Vittorio Emanuele - Gela (CL)", "peso": 0.02},

    # --- ENNA E PROVINCIA (Peso totale: 0.03) ---
    {"id": "OSP_UMBERTO_EN", "nome": "Umberto I - Enna", "peso": 0.02},
    {"id": "OSP_PIAZZA_EN", "nome": "Chiello - Piazza Armerina (EN)", "peso": 0.01},
]

# Distribuzione statistica dei codici di emergenza
CODICI_TRIAGE = [
    {"codice": "Rosso", "peso": 0.03},
    {"codice": "Arancione", "peso": 0.12},
    {"codice": "Giallo", "peso": 0.35},
    {"codice": "Verde", "peso": 0.42},
    {"codice": "Bianco", "peso": 0.08},
]

SINTOMI_MAP = {
    "Rosso": ["Arresto cardiaco", "Politrauma", "Ictus acuto", "Insufficienza respiratoria"],
    "Arancione": ["Dolore toracico", "Frattura esposta", "Alterazione coscienza"],
    "Giallo": ["Febbre alta", "Vomito persistente", "Trauma cranico lieve"],
    "Verde": ["Ferita lacera", "Lombalgia", "Gastroenterite"],
    "Bianco": ["Mal di gola", "Richiesta certificato", "Ansia"],
}

STATUS = ["In attesa", "In visita", "In osservazione"]

def weighted_choice(options: list, key: str = "peso") -> dict:
    """Utility function per l'estrazione pesata da una lista di dizionari."""
    pesi = [o[key] for o in options]
    return random.choices(options, weights=pesi, k=1)[0]

def get_arrival_weight(ora: int, mese: int) -> float:
    """
    Business Logic: Calcola il moltiplicatore di afflusso.
    Applica picchi alle 9-12 e 18-22. Aumenta il carico del 30% in estate.
    """
    ora_weight = {
        0:0.3, 1:0.2, 2:0.2, 3:0.2, 4:0.2, 5:0.3,
        6:0.5, 7:0.7, 8:0.9, 9:1.0, 10:1.0, 11:0.9,
        12:0.8, 13:0.7, 14:0.7, 15:0.8, 16:0.8, 17:0.9,
        18:1.0, 19:1.0, 20:0.9, 21:0.8, 22:0.6, 23:0.4,
    }
    stagione_moltiplicatore = 1.3 if mese in [6, 7, 8] else 1.0
    return ora_weight[ora] * stagione_moltiplicatore

def generate_admission(timestamp: datetime) -> dict:
    """Crea il record JSON per un singolo accesso in Pronto Soccorso."""
    ospedale = weighted_choice(OSPEDALI)
    triage = weighted_choice(CODICI_TRIAGE)
    codice = triage["codice"]

    # stima dei tempi di attesa basati su gravità
    attesa_base = {"Rosso": 0, "Arancione": 10, "Giallo": 45, "Verde": 120, "Bianco": 180}
    rumore_statistico = random.randint(-10, 30)
    attesa_stimata = max(0, attesa_base[codice] + rumore_statistico)

    return {
        "id_accesso": f"ACC-{timestamp.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
        "timestamp_arrivo": timestamp.isoformat(),
        "id_ospedale": ospedale["id"],
        "nome_ospedale": ospedale["nome"],
        "codice_triage": codice,
        "eta_paziente": random.randint(1, 95),
        "sesso": random.choice(["M", "F"]),
        "sintomo_principale": random.choice(SINTOMI_MAP[codice]),
        "status": random.choice(STATUS),
        "ora_arrivo": timestamp.hour,
        "giorno_settimana": timestamp.weekday(),
        "mese": timestamp.month,
        "attesa_stimata_minuti": attesa_stimata,
    }

def generate_batch(base_n: int = 50) -> list[dict]:
    """Genera un batch di accessi scalato in base all'orario e alla stagione."""
    now = datetime.now(timezone.utc)
    weight = get_arrival_weight(now.hour, now.month)
    
    # Adatta il numero di pazienti in base alla fascia oraria
    n_effettivo = max(1, int(base_n * weight))
    return [generate_admission(now) for _ in range(n_effettivo)]

if __name__ == "__main__":
    # Test esecuzione locale
    sample_batch = generate_batch(50)
    filename = f"sample_accessi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sample_batch, f, ensure_ascii=False, indent=2)
    print(f"✅ Test superato: generati {len(sample_batch)} accessi nel file locale {filename}")