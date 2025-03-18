import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from conn import get_db_connection

conn = get_db_connection()

df = pd.read_sql("""
SELECT data, ruota, primo, secondo, terzo, quarto, quinto 
FROM estrazioni ORDER BY data
""", conn)

def crea_sequenze(data, seq_length=50):
    sequenze, target = [], []
    for i in range(len(data) - seq_length):
        sequenze.append(data[i:i+seq_length])
        target.append(data[i+seq_length])
    return np.array(sequenze), np.array(target)

ruota = 'Bari'
df_ruota = df[df["ruota"] == ruota]

numeri = df_ruota[['primo', 'secondo', 'terzo', 'quarto', 'quinto']].values

scaler = MinMaxScaler()
numeri_scalati = scaler.fit_transform(numeri)

seq_length = 50
X, y = crea_sequenze(numeri_scalati, seq_length)

split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

model = Sequential([
    LSTM(64, input_shape=(X.shape[1], X.shape[2]), activation='relu'),
    Dense(5, activation='linear')
])

model.compile(optimizer='adam', loss='mse')

model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

ultima_sequenza = numeri_scalati[-seq_length:].reshape(1, seq_length, 5)
predizione = model.predict(ultima_sequenza)

predizione_numeri = scaler.inverse_transform(predizione).astype(int).flatten()

print(f"🔥 Numeri previsti per la prossima estrazione sulla ruota {ruota}: {predizione_numeri}")
