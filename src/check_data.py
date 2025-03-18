from data_loader import load_all_lotto_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = load_all_lotto_data()

# Controlliamo statistiche generali
print("Info dataset:")
print(df.info())

print("\nValori mancanti:")
print(df.isnull().sum())

plt.figure(figsize=(12, 6))
df.melt().value_counts().head(20).plot(kind='bar')
plt.title("Distribuzione dei numeri estratti negli ultimi 60 anni")
plt.show()
