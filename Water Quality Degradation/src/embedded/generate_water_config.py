import os
import joblib
import json
import numpy as np

def main():
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation"
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    # Load model
    pipeline = joblib.load(os.path.join(models_dir, "water_model.pkl"))
    with open(os.path.join(models_dir, "water_model_config.json"), "r") as f:
        config = json.load(f)
        
    features = config["features"]
    
    imputer = pipeline.named_steps['imputer']
    scaler = pipeline.named_steps['scaler']
    classifier = pipeline.named_steps['classifier']
    
    try:
        coefs = classifier.coef_
        intercepts = classifier.intercept_
        is_linear = True
    except AttributeError:
        coefs = None
        intercepts = None
        is_linear = False

    report = "# Water Quality Edge AI Deployment Prep\n\n"
    report += "This report compiles model coefficients, scaling configurations, and imputation constants for ESP32 microcontroller deployment.\n\n"
    
    report += "## Model Footprint\n"
    report += f"- **Base Estimator:** {config['model_type']}\n"
    report += f"- **Number of Features:** {len(features)}\n"
    
    report += "## Imputer Fill Constants (C-Array Format)\n"
    report += "```c\n"
    report += f"const float imputer_means[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in imputer.statistics_])}}};\n"
    report += "```\n\n"
    
    report += "## StandardScaler Parameters\n"
    report += "```c\n"
    report += f"const float scaler_means[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in scaler.mean_])}}};\n"
    report += f"const float scaler_scales[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in scaler.scale_])}}};\n"
    report += "```\n\n"
    
    if is_linear:
        report += "## Logistic Regression Weights (Class-wise C-arrays)\n"
        n_classes = coefs.shape[0]
        report += f"const int num_classes = {n_classes};\n\n"
        for i in range(n_classes):
            report += f"// Class {i} Weights\n"
            report += "```c\n"
            report += f"const float class_{i}_weights[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in coefs[i]])}}};\n"
            report += f"const float class_{i}_intercept = {intercepts[i]:.4f};\n"
            report += "```\n\n"
            
    report += "## Embedded Execution Strategy\n"
    report += "1. Sample sensors (pH, turbidity, EC, TDS, DHT22 temp).\n"
    report += "2. Compute rolling stats and rate features sequentially.\n"
    report += "3. Replace NaNs with `imputer_means`.\n"
    report += "4. Scale inputs using `scaler_means` and `scaler_scales`.\n"
    report += "5. Perform matrix dot product for each class probability.\n"
    
    with open(os.path.join(reports_dir, "water_edge_deployment_report.md"), "w") as f:
        f.write(report)
        
    print("Edge AI configuration generated successfully.")

if __name__ == "__main__":
    main()
