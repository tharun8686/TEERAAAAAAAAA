import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns

def construct_labels(df):
    """
    Constructs pseudo-labels for Industrial Emissions / Chemical Leak based on 
    gas response and particulate co-occurrence.
    Classes:
    0 = NORMAL (Clean air, low sensor responses)
    1 = WATCH (Low-level gas leak or PM elevation)
    2 = WARNING (Substantial leak or particulate surge)
    3 = CRITICAL (Severe toxic gas plume or dense chemical co-occurrence)
    """
    print("Constructing pseudo-labels...")
    
    # Rules
    conditions = [
        # CRITICAL
        (df['gas_response'] > 850) | (df['PM2.5'] > 150) | ((df['gas_response'] > 600) & (df['PM2.5'] > 100)) | (df['combined_emission_score'] > 85.0),
        # WARNING
        (df['gas_response'] > 500) | (df['PM2.5'] > 75) | (df['combined_emission_score'] > 30.0),
        # WATCH
        (df['gas_response'] > 300) | (df['PM2.5'] > 35) | (df['combined_emission_score'] > 10.0)
    ]
    choices = [3, 2, 1]
    
    df['risk_level'] = np.select(conditions, choices, default=0)
    print("Class distribution:")
    print(df['risk_level'].value_counts())
    return df

def train_and_evaluate(X_train, y_train, X_test, y_test, model_name, model):
    print(f"\nTraining {model_name}...")
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', model)
    ])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    print(f"--- {model_name} Results ---")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    metrics = {
        'model': model_name,
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0),
        'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
        'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0)
    }
    
    return pipeline, metrics, confusion_matrix(y_test, y_pred)

def main():
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions"
    in_path = os.path.join(base_dir, "data", "intermediate", "industrial_features.csv")
    out_table = os.path.join(base_dir, "data", "final", "industrial_training_table.csv")
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    os.makedirs(os.path.dirname(out_table), exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    df = pd.read_csv(in_path, index_col='sample_id')
    df = construct_labels(df)
    
    # Save final training table
    df.to_csv(out_table)
    
    # Exclude leakage descriptors to avoid trivial scaling mappings
    features = [
        'gas_response', 'smoke_or_proxy_response', 'PM2.5', 'PM10',
        'temperature_c', 'humidity', 'pressure',
        'gas_rate', 'PM2.5_rate', 'PM10_rate',
        'rolling_mean_gas', 'rolling_mean_PM2.5',
        'rolling_std_gas', 'rolling_std_PM2.5',
        'gas_spike_score', 'particulate_spike_score',
        'persistence_score'
    ]
    
    target = 'risk_level'
    
    # Split: Chronological chronological split is best as it mimics time sequence
    n = len(df)
    train_size = int(n * 0.7)
    val_size = int(n * 0.15)
    
    train_df = df.iloc[:train_size]
    val_df = df.iloc[train_size:train_size+val_size]
    test_df = df.iloc[train_size+val_size:]
    
    X_train, y_train = train_df[features], train_df[target]
    X_val, y_val = val_df[features], val_df[target]
    X_test, y_test = test_df[features], test_df[target]
    
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=10, class_weight='balanced', random_state=42)
    }
    
    results = []
    best_f1 = 0
    best_model_name = ""
    best_pipeline = None
    
    for name, model in models.items():
        pipeline, metrics, cm = train_and_evaluate(X_train, y_train, X_val, y_val, name, model)
        results.append(metrics)
        
        if metrics['f1_macro'] > best_f1:
            best_f1 = metrics['f1_macro']
            best_model_name = name
            best_pipeline = pipeline
            
    # Save model comparison
    pd.DataFrame(results).to_csv(os.path.join(reports_dir, "industrial_model_comparison.csv"), index=False)
    print(f"\nBest model selected: {best_model_name}")
    
    # Feature Importance for Random Forest
    if best_model_name == "RandomForest":
        importances = best_pipeline.named_steps['classifier'].feature_importances_
        feature_importance_df = pd.DataFrame({
            'Feature': features,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)
        
        feature_importance_df.to_csv(os.path.join(reports_dir, "industrial_feature_importance.csv"), index=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance_df)
        plt.title('Feature Importance (Random Forest)')
        plt.tight_layout()
        plt.savefig(os.path.join(reports_dir, "industrial_feature_importance.png"))
        
    # Save best model
    joblib.dump(best_pipeline, os.path.join(models_dir, "industrial_model.pkl"))
    
    config = {
        "model_type": best_model_name,
        "features": features,
        "classes": {
            0: "NORMAL",
            1: "WATCH",
            2: "WARNING",
            3: "CRITICAL"
        }
    }
    with open(os.path.join(models_dir, "industrial_model_config.json"), "w") as f:
        json.dump(config, f, indent=4)
        
    print("Training complete. Models and configurations saved.")

if __name__ == "__main__":
    main()
