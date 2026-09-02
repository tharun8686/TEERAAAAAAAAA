import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'intermediate', 'indofloods_master.csv')
    model_path = os.path.join(base_dir, 'models', 'severity_model_v1.pkl')

    print("Loading data...")
    df = pd.read_csv(data_path)

    # Filter target if needed, map target to binary
    # We assume 'Flood' -> 0, 'Severe Flood' -> 1
    df['Target'] = df['Flood Type'].map({'Flood': 0, 'Severe Flood': 1})
    
    # Drop rows without a valid target (if any)
    df = df.dropna(subset=['Target'])

    # Feature engineering (Precipitation)
    # T1d to T10d exist in the dataframe
    print("Engineering precipitation features...")
    df['T1d_T3d_ratio'] = df['T1d'] / (df['T3d'] + 1e-6)
    df['T3d_T10d_ratio'] = df['T3d'] / (df['T10d'] + 1e-6)
    df['short_term_acc'] = df['T1d'] + df['T2d'] + df['T3d']
    df['long_term_acc'] = df[['T1d', 'T2d', 'T3d', 'T4d', 'T5d', 'T6d', 'T7d', 'T8d', 'T9d', 'T10d']].sum(axis=1)
    df['rainfall_concentration'] = df['T1d'] / (df['long_term_acc'] + 1e-6)

    # Select base features
    precip_cols = ['T1d', 'T2d', 'T3d', 'T4d', 'T5d', 'T6d', 'T7d', 'T8d', 'T9d', 'T10d']
    derived_precip_cols = ['T1d_T3d_ratio', 'T3d_T10d_ratio', 'short_term_acc', 'long_term_acc', 'rainfall_concentration']
    
    catchment_cols = [
        'Drainage Area', 'Catchment Relief', 'Catchment Length', 'Drainage Density',
        'Stream Order', 'Form Factor', 'Circularity Ratio', 'Annual Precipitation',
        'Precipitation Seasonality', 'Soil type', 'Land cover', 'Urban percentage',
        'Population Density'
    ]

    all_features = precip_cols + derived_precip_cols + catchment_cols

    X = df[all_features].copy()
    y = df['Target']
    groups = df['GaugeID']

    # Step: Drop columns with > 50% missing
    print("Handling missing values (dropping > 50% missing columns)...")
    missing_pct = X.isnull().mean()
    cols_to_drop = missing_pct[missing_pct > 0.5].index.tolist()
    if cols_to_drop:
        print(f"Dropping high-missingness columns: {cols_to_drop}")
        X = X.drop(columns=cols_to_drop)

    # Remaining features after dropping
    remaining_features = X.columns.tolist()

    numeric_features = [c for c in remaining_features if c not in ['Soil type', 'Land cover', 'KoppenGeiger Climate Type', 'lithology type']]
    categorical_features = [c for c in remaining_features if c in ['Soil type', 'Land cover', 'KoppenGeiger Climate Type', 'lithology type']]

    # Step: Split by GaugeID
    print("Splitting data by GaugeID (80/20)...")
    gss = GroupShuffleSplit(n_splits=1, train_size=0.8, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    # Create preprocessing and modeling pipeline
    numeric_transformer = SimpleImputer(strategy='median')
    
    # Categorical imputer + OneHotEncoder
    # We replace missing with 'Unknown' string first
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=200, 
            min_samples_leaf=3,
            class_weight='balanced', 
            random_state=42,
            n_jobs=-1
        ))
    ])

    # Train model
    print("Training Random Forest Classifier...")
    model.fit(X_train, y_train)

    # Evaluate model
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    print("-" * 30)
    print("EVALUATION METRICS (Test Set)")
    print("-" * 30)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}  <-- FOCUS (Severe Flood)")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("-" * 30)

    # Save model
    print(f"Saving model to {model_path}...")
    joblib.dump(model, model_path)
    print("Done!")

if __name__ == "__main__":
    main()
