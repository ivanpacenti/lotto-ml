from conn import get_db_connection
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

# 📌 Connessione al database
conn = get_db_connection()

# 📥 Recuperiamo i dati dalla tabella `features_lotto`
query = """
SELECT data, ruota, numero, frequenza_totale, ritardo_medio_10, ritardo_medio_50, 
       mese, giorno, settimana, giorno_anno, giorno_settimana, 
       freq_ultime_10, freq_ultime_20, freq_ultime_50, freq_ultime_100, coppia_frequenza
FROM features_lotto
"""
df = pd.read_sql(query, conn)

df = df.sort_values(by=["data"])

features = ["frequenza_totale", "ritardo_medio_10", "ritardo_medio_50",
            "mese", "giorno", "settimana", "giorno_anno", "giorno_settimana",
            "freq_ultime_10", "freq_ultime_20", "freq_ultime_50", "freq_ultime_100", "coppia_frequenza"]
X = df[features]
y = df["numero"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = xgb.XGBClassifier()
model.load_model("modello_xgboost.json")  # Assumiamo che il modello sia stato salvato prima

ultima_data = df["data"].max()
prossima_data = ultima_data + pd.Timedelta(days=2)  # Supponiamo un'estrazione ogni 2 giorni

nuova_estrazione = pd.DataFrame({
    "frequenza_totale": np.random.randint(0, 500, 10),
    "ritardo_medio_10": np.random.randint(0, 50, 10),
    "ritardo_medio_50": np.random.randint(0, 50, 10),
    "mese": prossima_data.month,
    "giorno": prossima_data.day,
    "settimana": prossima_data.isocalendar().week,
    "giorno_anno": prossima_data.dayofyear,
    "giorno_settimana": prossima_data.weekday,
    "freq_ultime_10": np.random.randint(0, 10, 10),
    "freq_ultime_20": np.random.randint(0, 20, 10),
    "freq_ultime_50": np.random.randint(0, 50, 10),
    "freq_ultime_100": np.random.randint(0, 100, 10),
    "coppia_frequenza": np.random.randint(0, 50, 10)
})

nuova_estrazione_scaled = scaler.transform(nuova_estrazione)

previsione_numeri = model.predict(nuova_estrazione_scaled)

print(f"🔮 Numeri suggeriti per la prossima estrazione: {previsione_numeri}")
