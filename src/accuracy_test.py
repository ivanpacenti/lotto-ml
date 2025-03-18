import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from conn import get_db_connection


conn = get_db_connection()

# 📥 Recuperiamo i dati dalla tabella `features_lotto`
query = """
SELECT data, ruota, numero, frequenza_totale, ritardo_medio_10, ritardo_medio_50, 
       mese, giorno, settimana, giorno_anno, giorno_settimana, 
       freq_ultime_10, freq_ultime_20, freq_ultime_50, freq_ultime_100, coppia_frequenza
FROM features_lotto
"""
df = pd.read_sql(query, conn)

# 📆 Ordinamento dati per rispettare la sequenza temporale
df = df.sort_values(by=["data"])

# 🛠️ Preparazione features e target
features = [
    "frequenza_totale", "ritardo_medio_10", "ritardo_medio_50",
    "mese", "giorno", "settimana", "giorno_anno", "giorno_settimana",
    "freq_ultime_10", "freq_ultime_20", "freq_ultime_50", "freq_ultime_100", "coppia_frequenza"
]

X = df[features]
y = df["numero"] - 1

# 🔄 Normalizzazione con StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test, ruota_train, ruota_test = train_test_split(
    X_scaled, y, df["ruota"], test_size=0.2, shuffle=False
)

best_model = xgb.XGBClassifier()
best_model.load_model("modello_xgboost_finale.json")
# 📤 Caricamento del modello e scaler salvati
best_model = xgb.XGBClassifier()
best_model.load_model("modello_xgboost_finale.json")
scaler = joblib.load("scaler_lotto.pkl")

ultima_data = df["data"].max()

prossima_estrazione = df[df["data"] == ultima_data].copy()

numeri_per_ruota = {}

for ruota in prossima_estrazione["ruota"].unique():
    dati_ruota = prossima_estrazione[prossima_estrazione["ruota"] == ruota][features]
    dati_scalati = scaler.transform(dati_ruota)

    # Prevedi probabilità
    probs = best_model.predict_proba(dati_scalati)[0]

    # Numeri caldi (top 5)
    numeri_caldi = probs.argsort()[-5:][::-1] + 1
    numeri_per_ruota[ruota] = numeri_caldi

for ruota, numeri in numeri_per_ruota.items():
    print(f"🔥 Numeri caldi per {ruota}: {numeri}")
