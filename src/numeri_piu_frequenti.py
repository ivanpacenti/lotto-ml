# Importiamo la connessione al database
from conn import get_db_connection
import pandas as pd
import matplotlib.pyplot as plt


# Otteniamo la connessione
conn = get_db_connection()

# Query per ottenere la frequenza di tutti i numeri estratti
query = """
SELECT primo AS numero FROM estrazioni
UNION ALL
SELECT secondo FROM estrazioni
UNION ALL
SELECT terzo FROM estrazioni
UNION ALL
SELECT quarto FROM estrazioni
UNION ALL
SELECT quinto FROM estrazioni
"""

df = pd.read_sql(query, conn)

conn.close()

frequenza_numeri = df["numero"].value_counts(ascending=False)

plt.figure(figsize=(12, 6))
frequenza_numeri.plot(kind="bar", width=0.8)
plt.title("Frequenza dei Numeri Estratti")
plt.xlabel("Numero")
plt.ylabel("Frequenza")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()
