import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, precision_recall_curve, auc, confusion_matrix, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

def train_baseline_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    features_path = os.path.join(base_dir, 'data', 'intermediate', 'fire_features.csv')
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("Loading engineered features dataset...")
    df = pd.read_csv(features_path)

    # Sort chronologically by timestamp
    df.sort_values(by='timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Separate features and target
    X = df.drop(columns=['timestamp', 'fire_alarm'])
    y = df['fire_alarm']

    feature_names = X.columns.tolist()

    # Episode-Based Chronological Data Splitting
    # Episode 1 (Rows 0 to 24,993): Train set (Block 1 Normal + Block 2 Fire)
    # Episode 2 (Rows 24,994 to 62,629): Split into Val (24,994 to 43,811) and Test (43,812 to 62,629)
    train_end = 24994
    val_end = 43812

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    # Save split documentation report
    split_report_path = os.path.join(reports_dir, 'fire_split.md')
    with open(split_report_path, 'w', encoding='utf-8') as f:
        f.write("# Episode-Level Chronological Data Splitting Report\n\n")
        f.write(f"- **Total Dataset Size:** `{len(df):,}` samples\n")
        f.write(f"- **Training Split (Episode 1):** `{len(X_train):,}` samples (Index `0` to `{train_end-1}`)\n")
        f.write(f"  └─ Fire Alarm Balance: `{y_train.value_counts().to_dict()}`\n")
        f.write(f"- **Validation Split (Episode 2 - Early):** `{len(X_val):,}` samples (Index `{train_end}` to `{val_end-1}`)\n")
        f.write(f"  └─ Fire Alarm Balance: `{y_val.value_counts().to_dict()}`\n")
        f.write(f"- **Test Split (Episode 2 - Late & Recovery):** `{len(X_test):,}` samples (Index `{val_end}` to `{len(df)-1}`)\n")
        f.write(f"  └─ Fire Alarm Balance: `{y_test.value_counts().to_dict()}`\n")
        f.write("\n*Episode-level chronological splitting ensures realistic time-ordering without data leakage between episodes.*\n")

    print(f"Data split complete: Train ({len(X_train)}), Val ({len(X_val)}), Test ({len(X_test)})")

    # 2. Normalization: Fit StandardScaler ONLY on X_train
    print("Fitting StandardScaler ONLY on training set...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    scaler_path = os.path.join(models_dir, 'fire_scaler.pkl')
    joblib.dump(scaler, scaler_path)

    # 3. Train RandomForest Baseline Model
    print("Training RandomForestClassifier baseline (n_estimators=200, class_weight='balanced')...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)

    # 4. Evaluate Model on Test Set
    print("Evaluating baseline model on Chronological Test Set...")
    y_test_pred = rf_model.predict(X_test_scaled)
    y_test_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

    acc = accuracy_score(y_test, y_test_pred)
    prec = precision_score(y_test, y_test_pred, zero_division=0)
    rec = recall_score(y_test, y_test_pred, zero_division=0) # FOCUS METRIC: Fire Recall
    f1 = f1_score(y_test, y_test_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_test_proba)
    
    prec_array, rec_array, _ = precision_recall_curve(y_test, y_test_proba)
    pr_auc = auc(rec_array, prec_array)

    cm = confusion_matrix(y_test, y_test_pred)
    tn, fp, fn, tp = cm.ravel()
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    print("-" * 45)
    print("PHASE 3: RANDOM FOREST BASELINE TEST RESULTS")
    print("-" * 45)
    print(f"Accuracy:            {acc:.4f}")
    print(f"Precision:           {prec:.4f}")
    print(f"Recall (Fire=1):     {rec:.4f}  <-- FOCUS METRIC")
    print(f"F1-Score:            {f1:.4f}")
    print(f"ROC-AUC:             {roc_auc:.4f}")
    print(f"PR-AUC:              {pr_auc:.4f}")
    print(f"False Negative Rate: {fnr:.4f}")
    print(f"False Positive Rate: {fpr:.4f}")
    print("\nConfusion Matrix:")
    print(f"TN: {tn} | FP: {fp}\nFN: {fn} | TP: {tp}")
    print("-" * 45)

    # 5. Feature Importances
    importances = rf_model.feature_importances_
    fi_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    fi_df.sort_values(by='importance', ascending=False, inplace=True)
    fi_path = os.path.join(reports_dir, 'fire_feature_importance.csv')
    fi_df.to_csv(fi_path, index=False)

    # 6. Save Plot Artifacts
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal (0)', 'Fire (1)'], yticklabels=['Normal (0)', 'Fire (1)'])
    plt.title('Baseline Random Forest - Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'fire_confusion_matrix.png'))
    plt.close()

    plt.figure(figsize=(6, 5))
    fpr_vals, tpr_vals, _ = roc_curve(y_test, y_test_proba)
    plt.plot(fpr_vals, tpr_vals, label=f'ROC Curve (AUC = {roc_auc:.4f})', color='darkorange', lw=2)
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Baseline Random Forest - ROC Curve')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'fire_roc_curve.png'))
    plt.close()

    plt.figure(figsize=(6, 5))
    plt.plot(rec_array, prec_array, label=f'PR Curve (AUC = {pr_auc:.4f})', color='green', lw=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Baseline Random Forest - Precision-Recall Curve')
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, 'fire_pr_curve.png'))
    plt.close()

    # 7. Save Model & Config JSON
    model_path = os.path.join(models_dir, 'fire_random_forest.pkl')
    joblib.dump(rf_model, model_path)

    config_data = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "class_weight": "balanced",
        "n_features": len(feature_names),
        "feature_names": feature_names,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_std": scaler.scale_.tolist(),
        "severity_thresholds": {
            "0.00-0.50": "NORMAL",
            "0.50-0.70": "WATCH",
            "0.70-0.85": "WARNING",
            "0.85-1.00": "CRITICAL"
        },
        "test_metrics": {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "fnr": float(fnr),
            "fpr": float(fpr)
        }
    }

    config_path = os.path.join(models_dir, 'fire_model_config.json')
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    # 8. Save Detailed Model Report
    report_path = os.path.join(reports_dir, 'fire_model_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Phase 3: Baseline Random Forest Model Report\n\n")
        f.write("## Test Metrics (Unseen Chronological Split)\n")
        f.write(f"- **Accuracy:** `{acc:.4f}`\n")
        f.write(f"- **Precision:** `{prec:.4f}`\n")
        f.write(f"- **Recall (Fire Class = 1):** `{rec:.4f}` *(Focus Metric)*\n")
        f.write(f"- **F1-Score:** `{f1:.4f}`\n")
        f.write(f"- **ROC-AUC:** `{roc_auc:.4f}`\n")
        f.write(f"- **PR-AUC:** `{pr_auc:.4f}`\n")
        f.write(f"- **False Negative Rate:** `{fnr:.4f}`\n")
        f.write(f"- **False Positive Rate:** `{fpr:.4f}`\n\n")
        f.write("## Confusion Matrix\n")
        f.write(f"```text\nTrue Normal (TN): {tn:,}  |  False Positive (FP): {fp:,}\nFalse Negative (FN): {fn:,}  |  True Fire (TP): {tp:,}\n```\n\n")
        f.write("## Top 10 Most Important Features\n```text\n")
        f.write(fi_df.head(10).to_string(index=False))
        f.write("\n```\n")

    print("Phase 3 baseline model training complete!")

if __name__ == '__main__':
    train_baseline_model()
