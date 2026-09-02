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
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns

def construct_labels(df):
    """
    Constructs pseudo-labels for Water Quality Degradation.
    Classes:
    0 = NORMAL (Complies with WHO/IS 10500 standards)
    1 = WATCH (Low-level index threshold warnings)
    2 = WARNING (Substantial degradation in physical or chemical properties)
    3 = CRITICAL (Severe contamination, extreme acidity/alkalinity, high turbidity, or oxygen depletion)
    """
    print("Constructing pseudo-labels...")
    
    # Rules based on physical safety bounds
    conditions = [
        # CRITICAL
        (df['pH'] < 4.5) | (df['pH'] > 10.5) | (df['turbidity'] > 50.0) | (df['TDS'] > 1200.0) | (df['dissolved_oxygen'] < 2.0) | (df['combined_water_quality_score'] > 500.0),
        # WARNING
        (df['pH'] < 5.5) | (df['pH'] > 9.5) | (df['turbidity'] > 15.0) | (df['TDS'] > 600.0) | (df['dissolved_oxygen'] < 4.0) | (df['combined_water_quality_score'] > 150.0),
        # WATCH
        (df['pH'] < 6.5) | (df['pH'] > 8.5) | (df['turbidity'] > 5.0) | (df['TDS'] > 300.0) | (df['dissolved_oxygen'] < 6.0) | (df['combined_water_quality_score'] > 50.0)
    ]
    choices = [3, 2, 1]
    
    df['risk_level'] = np.select(conditions, choices, default=0)
    print("Class distribution:")
    print(df['risk_level'].value_counts())
    return df

def train_and_evaluate(X_train, y_train, X_test, y_test, model_name, model):
    print(f"\nTraining {model_name}...")
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
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
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation"
    in_path = os.path.join(base_dir, "data", "intermediate", "water_features.csv")
    out_table = os.path.join(base_dir, "data", "final", "water_training_table.csv")
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    os.makedirs(os.path.dirname(out_table), exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    df = pd.read_csv(in_path, index_col='sample_id')
    df = construct_labels(df)
    
    # Save final training table
    df.to_csv(out_table)
    
    features = [
        'pH', 'turbidity', 'EC', 'TDS', 'dissolved_oxygen', 'temperature_c',
        'pH_rate', 'turbidity_rate', 'EC_rate', 'TDS_rate', 'DO_rate',
        'rolling_mean_pH', 'rolling_mean_turbidity', 'rolling_mean_EC', 'rolling_mean_TDS', 'rolling_mean_DO',
        'rolling_std_pH', 'rolling_std_turbidity', 'rolling_std_EC', 'rolling_std_TDS', 'rolling_std_DO',
        'acidity_shift_score', 'degradation_spike_score', 'conductivity_shift_score', 'oxygen_drop_score',
        'persistence_score'
    ]
    
    target = 'risk_level'
    
    # Split
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
    pd.DataFrame(results).to_csv(os.path.join(reports_dir, "water_model_comparison.csv"), index=False)
    print(f"\nBest model selected: {best_model_name}")
    
    # Feature Importance for Random Forest
    if best_model_name == "RandomForest":
        importances = best_pipeline.named_steps['classifier'].feature_importances_
        feature_importance_df = pd.DataFrame({
            'Feature': features,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)
        
        feature_importance_df.to_csv(os.path.join(reports_dir, "water_feature_importance.csv"), index=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance_df)
        plt.title('Feature Importance (Random Forest)')
        plt.tight_layout()
        plt.savefig(os.path.join(reports_dir, "water_feature_importance.png"))
        
    # Save best model
    joblib.dump(best_pipeline, os.path.join(models_dir, "water_model.pkl"))
    
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
    with open(os.path.join(models_dir, "water_model_config.json"), "w") as f:
        json.dump(config, f, indent=4)
        
    print("Training complete. Models and configurations saved.")

if __name__ == "__main__":
    main()
