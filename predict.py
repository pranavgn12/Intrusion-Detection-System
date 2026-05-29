import pandas as pd
import joblib

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =====================================
# LOAD MODEL
# =====================================

model = joblib.load(
    "ids_rf_model.pkl"
)

encoder = joblib.load(
    "label_encoder.pkl"
)

# =====================================
# LOAD DATASET
# =====================================

df = pd.read_csv(
    "ftp_t.csv"
)

# =====================================
# FEATURES / LABELS
# =====================================

X = df.drop(
    columns=["label"]
)

y_true = df["label"]

# Convert labels to encoded form
y_true_encoded = encoder.transform(
    y_true
)

# =====================================
# PREDICT
# =====================================

y_pred_encoded = model.predict(
    X
)

y_pred = encoder.inverse_transform(
    y_pred_encoded
)

# =====================================
# ACCURACY
# =====================================

accuracy = accuracy_score(
    y_true_encoded,
    y_pred_encoded
)

print("\n=================================")
print("ACCURACY")
print("=================================")

print(
    f"{accuracy * 100:.2f}%"
)

# =====================================
# CORRECT / WRONG
# =====================================

correct = (
    y_true.values == y_pred
).sum()

wrong = len(y_true) - correct

print("\n=================================")
print("PREDICTION COUNTS")
print("=================================")

print("Correct :", correct)
print("Wrong   :", wrong)

# =====================================
# CLASSIFICATION REPORT
# =====================================

print("\n=================================")
print("CLASSIFICATION REPORT")
print("=================================")

print(
    classification_report(
        y_true,
        y_pred,
        digits=4
    )
)

# =====================================
# CONFUSION MATRIX
# =====================================

print("\n=================================")
print("CONFUSION MATRIX")
print("=================================")

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=encoder.classes_
)

cm_df = pd.DataFrame(
    cm,
    index=encoder.classes_,
    columns=encoder.classes_
)

print(cm_df)

# =====================================
# FEATURE IMPORTANCE
# =====================================

print("\n=================================")
print("TOP FEATURES")
print("=================================")

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print(
    importance_df.head(20)
)

# =====================================
# SAMPLE PREDICTIONS
# =====================================

print("\n=================================")
print("FIRST 20 PREDICTIONS")
print("=================================")

result_df = pd.DataFrame({
    "Actual": y_true.values,
    "Predicted": y_pred
})

print(
    result_df.head(20)
)
