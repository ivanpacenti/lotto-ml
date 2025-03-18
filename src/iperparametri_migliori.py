import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import joblib
from conn import get_db_connection

conn = get_db_connection()

query = """
SELECT data, ruota, numero, frequenza_totale, ritardo_medio_10, ritardo_medio_50, 
       mese, giorno, settimana, giorno_anno, giorno_settimana, 
       freq_ultime_10, freq_ultime_20, freq_ultime_50, freq_ultime_100, coppia_frequenza
FROM features_lotto
"""
df = pd.read_sql(query, conn)

df = df.sort_values(by=["data"])

features = [
    "frequenza_totale", "ritardo_medio_10", "ritardo_medio_50",
    "mese", "giorno", "settimana", "giorno_anno", "giorno_settimana",
    "freq_ultime_10", "freq_ultime_20", "freq_ultime_50", "freq_ultime_100", "coppia_frequenza"
]

X = df[features]
y = df["numero"] - 1

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

xgb_model = xgb.XGBClassifier(
    objective="multi:softmax",
    num_class=90,
    tree_method="hist",
    device="cuda",
    eval_metric="mlogloss"
)

param_grid = {
    "n_estimators": [100, 500],
    "max_depth": [3, 5],
    "learning_rate": [0.1],
    "subsample": [1.0],
    "colsample_bytree": [1.0]
}


grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    cv=3,
    scoring="accuracy",
    verbose=2,
    n_jobs=1
)

print("🚀 Avvio Grid Search con GPU...")
grid_search.fit(X_train, y_train)

print("🔍 Migliori parametri:", grid_search.best_params_)
print(f"🎯 Accuracy migliore: {grid_search.best_score_:.4f}")

best_model = grid_search.best_estimator_
best_model_filename = "modello_xgboost_finale.json"
scaler_filename = "scaler_lotto.pkl"

best_model.save_model(best_model_filename)
joblib.dump(scaler, scaler_filename)

print(f"✅ Modello salvato come '{best_model_filename}'")
print(f"✅ Scaler salvato come '{scaler_filename}'")
