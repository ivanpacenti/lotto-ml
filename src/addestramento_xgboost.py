import xgboost as xgb
from sklearn.metrics import accuracy_score

from src.estrazione_da_modello import X_train, y_train, X_test, y_test

model = xgb.XGBClassifier(
    objective="multi:softmax", num_class=91,  # 90 numeri più 1 classe extra
    n_estimators=500, learning_rate=0.1, max_depth=5
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Accuracy del modello: {accuracy:.4f}")
