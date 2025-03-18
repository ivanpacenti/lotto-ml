from conn import get_db_connection
import pandas as pd
import numpy as np

# 📌 Connessione al database
conn = get_db_connection()

# 📥 Recuperiamo i dati dalla tabella `estrazioni`
query = """
SELECT anno, data, ruota, primo, secondo, terzo, quarto, quinto 
FROM estrazioni
"""
df = pd.read_sql(query, conn)

# 📆 Convertiamo la colonna data in formato datetime
df["data"] = pd.to_datetime(df["data"])

# 🎯 Creiamo nuove feature temporali
df["mese"] = df["data"].dt.month
df["giorno"] = df["data"].dt.day
df["settimana"] = df["data"].dt.isocalendar().week
df["giorno_anno"] = df["data"].dt.dayofyear
df["giorno_settimana"] = df["data"].dt.weekday  # 0 = Lunedì, 6 = Domenica

# 🔢 Trasformiamo i dati in formato lungo (un numero per riga)
numeri = pd.melt(df, id_vars=["anno", "data", "ruota", "mese", "giorno", "settimana", "giorno_anno", "giorno_settimana"],
                 value_vars=["primo", "secondo", "terzo", "quarto", "quinto"],
                 var_name="posizione", value_name="numero")

# 📊 Calcoliamo la frequenza totale di ogni numero
numeri["frequenza_totale"] = numeri.groupby(["ruota", "numero"], group_keys=False).cumcount() + 1

# ⏳ Calcoliamo il ritardo di ogni numero (giorni dall'ultima uscita)
numeri["ritardo"] = numeri.groupby(["ruota", "numero"], group_keys=False)["data"].diff().dt.days.fillna(0)

# 📈 **Calcoliamo il ritardo medio nelle ultime 10 e 50 estrazioni con `transform()`**
numeri["ritardo_medio_10"] = numeri.groupby(["ruota", "numero"])["ritardo"].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
numeri["ritardo_medio_50"] = numeri.groupby(["ruota", "numero"])["ritardo"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# 📊 Frequenza nelle ultime 10, 20, 50, 100 estrazioni
for window in [10, 20, 50, 100]:
    numeri[f"freq_ultime_{window}"] = numeri.groupby(["ruota", "numero"])["numero"].transform(lambda x: x.rolling(window=window, min_periods=1).count())

# 🔗 Coppie di numeri più frequenti
coppie = numeri.groupby(["ruota", "data"])["numero"].apply(list).reset_index()
coppie["coppia"] = coppie["numero"].apply(lambda x: list(zip(x[:-1], x[1:])))  # Creiamo coppie di numeri consecutivi
coppie_exploded = coppie.explode("coppia").dropna()
coppie_exploded[["num1", "num2"]] = pd.DataFrame(coppie_exploded["coppia"].tolist(), index=coppie_exploded.index)

# 📊 Calcoliamo la frequenza delle coppie più estratte
coppie_freq = coppie_exploded.groupby(["ruota", "num1", "num2"]).size().reset_index(name="coppia_frequenza")

# 📥 Uniamo la frequenza delle coppie al dataset principale
numeri = numeri.merge(coppie_freq, left_on=["ruota", "numero"], right_on=["ruota", "num1"], how="left").drop(columns=["num1", "num2"]).fillna(0)

# 🔄 Pulizia finale: sostituiamo eventuali NaN con 0
numeri.fillna(0, inplace=True)

# 📥 Prepariamo i dati per l'inserimento nel database
records_to_insert = numeri[[
    "anno", "data", "ruota", "numero", "frequenza_totale", "ritardo_medio_10", "ritardo_medio_50", 
    "mese", "giorno", "settimana", "giorno_anno", "giorno_settimana",
    "freq_ultime_10", "freq_ultime_20", "freq_ultime_50", "freq_ultime_100", "coppia_frequenza"
]].values.tolist()

# 🗑 Svuotiamo la tabella `features_lotto` prima di reinserire i dati
with conn.cursor() as cursor:
    cursor.execute("DELETE FROM features_lotto")
    conn.commit()

# 🏛 Query SQL per reinserire i dati nella tabella
insert_query = """
INSERT INTO features_lotto 
(anno, data, ruota, numero, frequenza_totale, ritardo_medio_10, ritardo_medio_50, 
 mese, giorno, settimana, giorno_anno, giorno_settimana, 
 freq_ultime_10, freq_ultime_20, freq_ultime_50, freq_ultime_100, coppia_frequenza)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

BATCH_SIZE = 1000  # Numero di righe da inserire per batch

with conn.cursor() as cursor:
    for i in range(0, len(records_to_insert), BATCH_SIZE):
        batch = records_to_insert[i:i+BATCH_SIZE]
        cursor.executemany(insert_query, batch)
        conn.commit()  # Commit dopo ogni batch
        print(f"✅ Inserite {i + len(batch)} righe su {len(records_to_insert)}")

