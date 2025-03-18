from conn import get_db_connection
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

conn = get_db_connection()

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

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

print(f"✅ Dati pronti! Train set: {len(X_train)} | Test set: {len(X_test)}")
