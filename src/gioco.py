from conn import get_db_connection
import pandas as pd

conn = get_db_connection()

query = """
SELECT ruota, numero, frequenza_totale, ritardo_medio 
FROM features_lotto
WHERE data = (SELECT MAX(data) FROM features_lotto)
ORDER BY ruota, (frequenza_totale / (ritardo_medio + 1)) DESC
"""

df = pd.read_sql(query, conn)

numeri_per_ruota = df.groupby("ruota").apply(lambda x: x.drop_duplicates(subset=["numero"]).head(5)).reset_index(drop=True)

for ruota, gruppo in numeri_per_ruota.groupby("ruota"):
    numeri = ", ".join(map(str, gruppo["numero"].tolist()))
    print(f"🎯 Ruota {ruota}: {numeri}")
