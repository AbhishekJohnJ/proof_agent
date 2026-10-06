import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from catboost import CatBoostClassifier

from backend.ml.features import prepare_prediction_dataset, extract_features_and_target, FORBIDDEN_LEAKAGE_COLUMNS

def train_model():
    data_dir = Path("data")
    models_dir = Path("models")
    results_dir = Path("results")

    models_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    print("Loading datasets from data/...")
    orders_df = pd.read_csv(data_dir / "orders.csv")
    returns_df = pd.read_csv(data_dir / "returns.csv")
    customers_df = pd.read_csv(data_dir / "customers.csv")
    order_items_df = pd.read_csv(data_dir / "order_items.csv")
    products_df = pd.read_csv(data_dir / "products.csv")

    print(f"Loaded {len(orders_df)} orders, {len(returns_df)} returns.")

    # 1. Prepare prediction dataset
    prepared_df = prepare_prediction_dataset(orders_df, returns_df, customers_df, order_items_df, products_df)

    # 2. Extract features & target
    X, y, feature_names, cat_features = extract_features_and_target(prepared_df, is_training=True)

    for forbidden in FORBIDDEN_LEAKAGE_COLUMNS:
        assert forbidden not in X.columns, f"Target leakage validation error: {forbidden} present in X!"

    print(f"Extracted {len(feature_names)} features for {len(X)} instances (Target return rate: {y.mean()*100:.2f}%).")

    # 3. Stratified Train-Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 4. Train CatBoostClassifier with class balancing
    print("Training CatBoostClassifier...")
    model = CatBoostClassifier(
        iterations=350,
        depth=6,
        learning_rate=0.08,
        auto_class_weights="Balanced",
        random_seed=42,
        cat_features=cat_features,
        verbose=False
    )
    model.fit(X_train, y_train)

    # 5. Evaluate on Test Set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": cm
    }

    print("Training complete. Evaluation Metrics:")
    print(json.dumps(metrics, indent=2))

    # 6. Save Model Artifact
    model_path = models_dir / "return_prediction_model.cbm"
    model.save_model(str(model_path))
    print(f"Saved CatBoost model to {model_path}")

    # 7. Save Model Metadata
    metadata = {
        "model_name": "return_prediction_model",
        "model_type": "CatBoostClassifier",
        "training_dataset": "Indian E-Commerce Sales & Customer Analytics (orders.csv + returns.csv)",
        "training_timestamp": pd.Timestamp.now().isoformat(),
        "feature_names": feature_names,
        "categorical_features": cat_features,
        "target": "is_returned",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "metrics": metrics,
        "random_seed": 42,
        "model_version": "1.0.0",
        "forbidden_features_excluded": FORBIDDEN_LEAKAGE_COLUMNS
    }

    meta_path = models_dir / "return_prediction_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to {meta_path}")

    # 8. Save Feature Importance Artifact
    importances = model.get_feature_importance()
    fi_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)
    fi_path = results_dir / "feature_importance.csv"
    fi_df.to_csv(fi_path, index=False)
    print(f"Saved feature importances to {fi_path}")

    # Save metrics artifact
    with open(results_dir / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    train_model()
