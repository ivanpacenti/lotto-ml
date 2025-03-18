import pandas as pd
import os
from glob import glob

DATA_DIR = "../data/"


def load_all_lotto_data():

    excel_files = glob(os.path.join(DATA_DIR, "*.xls"))  # Cerca i file .xls
    print(f"Trovati {len(excel_files)} file.")

    all_data = []

    for file in excel_files:
        try:
            df = pd.read_excel(file, engine="xlrd")  # Usa xlrd per .xls
            df["file"] = os.path.basename(file)  # Aggiunge l'anno
            all_data.append(df)
        except Exception as e:
            print(f"❌ Errore con il file {file}: {e}")

    if not all_data:
        raise ValueError("Nessun file valido trovato!")

    full_df = pd.concat(all_data, ignore_index=True)

    print("Dataset combinato con successo!")
    print(full_df.head())

    return full_df


if __name__ == "__main__":
    df = load_all_lotto_data()
    print(f"Dimensioni dataset totale: {df.shape}")
