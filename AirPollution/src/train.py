import pandas as pd
import numpy as np
import os
import joblib
import json

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import (
    mean_absolute_error, root_mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

def train_and_evaluate_models(df):
    print("Training Model Baselines (Persistence, Ridge, Random Forest, Gradient Boosting)...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(os.path.join(models_dir, 'baseline'), exist_ok=True)
    os.makedirs(os.path.join(models_dir, 'reference'), exist_ok=True)
    os.makedirs(os.path.join(models_dir, 'edge'), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # Edge Features (Track B)
    edge_features = [
        'pm25', 'pm10', 'gas_proxy', 'temperature', 'relative_humidity', 'pressure',
        'pm25_lag_15', 'pm25_lag_30', 'pm25_delta_30', 'pm25_slope_30',
        'hour_sin', 'hour_cos'
    ]

    # Reference Features (Track A)
    ref_features = [
        'pm25', 'pm10', 'no', 'no2', 'nox', 'nh3', 'so2', 'co', 'o3',
        'temperature', 'relative_humidity', 'wind_speed', 'wind_direction_sin', 'wind_direction_cos',
        'pressure', 'pm25_lag_15', 'pm25_lag_30', 'pm25_lag_60', 'pm25_delta_30', 'pm25_slope_30',
        'hour_sin', 'hour_cos'
    ]

    # Fill any remaining NaNs safely with column medians
    for f in ref_features:
        if f in df.columns:
            df[f] = df[f].fillna(df[f].median() if not np.isnan(df[f].median()) else 0.0)

    # Chronological Split (70% train, 15% val, 15% test)
    df.sort_values(by='timestamp', inplace=True)
    n = len(df)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    df_train = df.iloc[:train_end]
    df_val = df.iloc[train_end:val_end]
    df_test = df.iloc[val_end:]

    print(f"Chronological Split: Train={len(df_train):,} | Val={len(df_val):,} | Test={len(df_test):,}")

    results = []

    # --- Baseline 1: Persistence Baseline ---
    y_test_pm25 = df_test['future_pm25_60m']
    y_pred_pers = df_test['pm25']
    mae_pers = mean_absolute_error(y_test_pm25, y_pred_pers)
    rmse_pers = root_mean_squared_error(y_test_pm25, y_pred_pers)
    r2_pers = r2_score(y_test_pm25, y_pred_pers)

    results.append({
        'track': 'Baseline',
        'model': 'Persistence',
        'task': 'Regression (60m PM2.5)',
        'mae': round(float(mae_pers), 2),
        'rmse': round(float(rmse_pers), 2),
        'r2': round(float(r2_pers), 4),
        'accuracy': 'N/A', 'precision': 'N/A', 'recall': 'N/A', 'f1': 'N/A'
    })

    # --- Track B: Edge Model (Random Forest Classifier & Regressor) ---
    X_train_edge = df_train[edge_features]
    y_train_reg = df_train['future_pm25_60m']
    y_train_cls = df_train['pollution_deterioration_60m']

    X_test_edge = df_test[edge_features]
    y_test_reg = df_test['future_pm25_60m']
    y_test_cls = df_test['pollution_deterioration_60m']

    scaler_edge = StandardScaler()
    X_train_edge_scaled = scaler_edge.fit_transform(X_train_edge)
    X_test_edge_scaled = scaler_edge.transform(X_test_edge)

    # Save Scaler
    joblib.dump(scaler_edge, os.path.join(models_dir, 'edge', 'scaler.pkl'))
    with open(os.path.join(models_dir, 'edge', 'scaler.json'), 'w') as f:
        json.dump({'mean': scaler_edge.mean_.tolist(), 'std': scaler_edge.scale_.tolist()}, f)

    # Edge Regression Model
    rf_reg = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train_edge_scaled, y_train_reg)
    y_pred_reg = rf_reg.predict(X_test_edge_scaled)

    mae_rf = mean_absolute_error(y_test_reg, y_pred_reg)
    rmse_rf = root_mean_squared_error(y_test_reg, y_pred_reg)
    r2_rf = r2_score(y_test_reg, y_pred_reg)

    results.append({
        'track': 'Track B (Edge)',
        'model': 'RandomForestRegressor',
        'task': 'Regression (60m PM2.5)',
        'mae': round(float(mae_rf), 2),
        'rmse': round(float(rmse_rf), 2),
        'r2': round(float(r2_rf), 4),
        'accuracy': 'N/A', 'precision': 'N/A', 'recall': 'N/A', 'f1': 'N/A'
    })

    # Edge Deterioration Classifier
    rf_cls = RandomForestClassifier(n_estimators=50, max_depth=10, class_weight='balanced', random_state=42, n_jobs=-1)
    rf_cls.fit(X_train_edge_scaled, y_train_cls)
    y_pred_cls = rf_cls.predict(X_test_edge_scaled)
    y_proba_cls = rf_cls.predict_proba(X_test_edge_scaled)[:, 1]

    acc = accuracy_score(y_test_cls, y_pred_cls)
    prec = precision_score(y_test_cls, y_pred_cls, zero_division=0)
    rec = recall_score(y_test_cls, y_pred_cls, zero_division=0)
    f1 = f1_score(y_test_cls, y_pred_cls, zero_division=0)
    roc_auc = roc_auc_score(y_test_cls, y_proba_cls)

    results.append({
        'track': 'Track B (Edge)',
        'model': 'RandomForestClassifier',
        'task': 'Classification (60m Deterioration)',
        'mae': 'N/A', 'rmse': 'N/A', 'r2': 'N/A',
        'accuracy': round(float(acc), 4),
        'precision': round(float(prec), 4),
        'recall': round(float(rec), 4),
        'f1': round(float(f1), 4),
        'roc_auc': round(float(roc_auc), 4)
    })

    joblib.dump(rf_cls, os.path.join(models_dir, 'edge', 'air_quality_model.pkl'))

    # Save Results Report
    df_res = pd.DataFrame(results)
    df_res.to_csv(os.path.join(reports_dir, 'model_comparison.csv'), index=False)
    
    print("-" * 60)
    print("AIR POLLUTION MODEL EVALUATION SUMMARY")
    print("-" * 60)
    print(df_res.to_string(index=False))
    print("-" * 60)

    # Save feature schema JSON
    with open(os.path.join(models_dir, 'edge', 'feature_schema.json'), 'w') as f:
        json.dump({'edge_features': edge_features, 'ref_features': ref_features}, f, indent=2)

    return df_res

if __name__ == '__main__':
    from data_loader import load_all_stations
    from cleaning import clean_and_validate_data
    from feature_engineering import generate_features
    from labels import generate_future_labels

    df_raw = load_all_stations()
    df_clean = clean_and_validate_data(df_raw)
    df_feats = generate_features(df_clean)
    df_labels = generate_future_labels(df_feats)
    train_and_evaluate_models(df_labels)
