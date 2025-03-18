import pandas as pd
import pyodbc
import re
from conn import get_db_connection


conn = get_db_connection()
cursor = conn.cursor()

file_path = "C:/Users/Ivan/PycharmProjects/PythonProject/data/2010.xls"

file_excel = pd.read_excel(file_path, header=None, engine="xlrd")  # Leggiamo senza intestazioni

anno=0

prima_cella = str(file_excel.iloc[0, 0])  # Convertiamo in stringa per sicurezza

match = re.search(r'\b\d{4}\b', prima_cella)
anno = int(match.group()) if match else None


# Trasformiamo i dati per adattarli alla struttura del DB
ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

dati_per_db = []

for index, row in file_excel.iloc[4:].iterrows():  # Saltiamo le prime 4 righe
    data_estrazione = row[0]
    a = 0


    for ruota in ruote:

        primo = row[a+1]
        secondo = row[a+2]
        terzo = row[a+3]
        quarto = row[a+4]
        quinto = row[a+5]
        a=a+5


        dati_per_db.append((anno, data_estrazione, ruota, primo, secondo, terzo, quarto, quinto))

# Query di inserimento
query = """
INSERT INTO lotto.dbo.estrazioni (anno, [data], ruota, primo, secondo, terzo, quarto, quinto)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

# Inseriamo i dati nel DB
cursor.executemany(query, dati_per_db)
conn.commit()

print(f"Inseriti {len(dati_per_db)} record nel database!")

# Chiudiamo la connessione
cursor.close()
conn.close()
