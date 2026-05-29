import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =====================================
# LOAD DATASETS
# =====================================

files = [
    "Nothing.csv",
    "nothing.csv",
    "portscan_test.csv",
    "portscan.csv",
    "portscan_2.csv",
    "portscan_3.csv",
    "portscan_4.csv",
    "portscan_5.csv",
    "reconnaissance_04.csv",
    "synflood.csv",
    "synflood_test.csv",
    "udpflood.csv",
    "icmpflood.csv",
    "arpspoofing.csv",
    "arpspoofing_2.csv",
    "arpspoofing_3.csv",
]

dfs = []

for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

data = pd.concat(
    dfs,
    ignore_index=True
)

print("\nDataset shape:")
print(data.shape)

print("\nClass counts:")
print(data["label"].value_counts())

# =====================================
# FEATURES / TARGET
# =====================================

X = data.drop(columns=["label"])

y = data["label"]

# =====================================
# ENCODE LABELS
# =====================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\nClasses:")
for i, cls in enumerate(label_encoder.classes_):
    print(i, "->", cls)

# # =====================================
# # TRAIN TEST SPLIT
# # =====================================
#
# X_train, X_test, y_train, y_test = train_test_split(
#     X,
#     y_encoded,
#     test_size=0.2,
#     random_state=42,
#     stratify=y_encoded
# )

# =====================================
# RANDOM FOREST
# =====================================

model = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    min_samples_leaf=1,
    min_samples_split=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
model.fit(
    X,
    y_encoded
)

# # =====================================
# # EVALUATION
# # =====================================
#
# y_pred = model.predict(X_test)
#
# accuracy = accuracy_score(
#     y_test,
#     y_pred
# )
#
# print("\nAccuracy:")
# print(f"{accuracy:.4f}")
#
# print("\nClassification Report:")
# print(
#     classification_report(
#         y_test,
#         y_pred,
#         target_names=label_encoder.classes_
#     )
# )
#
# print("\nConfusion Matrix:")
# print(
#     confusion_matrix(
#         y_test,
#         y_pred
#     )
# )

# =====================================
# FEATURE IMPORTANCE
# =====================================

print("\nTop Features:")

feature_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print(feature_importance.head(20))

# =====================================
# SAVE MODEL
# =====================================

joblib.dump(
    model,
    "ids_rf_model.pkl"
)

joblib.dump(
    label_encoder,
    "label_encoder.pkl"
)

print("\nSaved:")
print("ids_rf_model.pkl")

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
}).sort_values(
    by="importance",
    ascending=False
)

print(importance_df)
