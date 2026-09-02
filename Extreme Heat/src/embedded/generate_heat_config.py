import os
import joblib
import json

def main():
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat"
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    # Load model
    pipeline = joblib.load(os.path.join(models_dir, "heat_model.pkl"))
    
    with open(os.path.join(models_dir, "heat_model_config.json"), "r") as f:
        config = json.load(f)
        
    features = config["features"]
    
    scaler = pipeline.named_steps['scaler']
    classifier = pipeline.named_steps['classifier']
    
    # We assume LogisticRegression was chosen (as per earlier run). 
    # If it's RandomForest, exporting weights is not directly possible like this.
    try:
        coefs = classifier.coef_
        intercepts = classifier.intercept_
        is_linear = True
    except AttributeError:
        coefs = None
        intercepts = None
        is_linear = False

    report = "# Edge AI Deployment Preparation\n\n"
    report += "This report summarizes the model's footprint and parameters for deployment on a microcontroller (e.g., ESP32).\n\n"
    
    report += "## Model Architecture\n"
    report += f"- **Base Estimator:** {config['model_type']}\n"
    report += f"- **Number of Features:** {len(features)}\n"
    report += f"- **Target Classes:** {json.dumps(config['classes'])}\n\n"
    
    report += "## Standard Scaler Parameters (C-Array Format)\n"
    report += "```c\n"
    report += f"const float scaler_means[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in scaler.mean_])}}};\n"
    report += f"const float scaler_scales[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in scaler.scale_])}}};\n"
    report += "```\n\n"
    
    if is_linear:
        report += "## Logistic Regression Weights (C-Array Format)\n"
        n_classes = coefs.shape[0]
        report += f"const int num_classes = {n_classes};\n\n"
        for i in range(n_classes):
            report += f"// Class {i} Weights\n"
            report += "```c\n"
            report += f"const float class_{i}_weights[{len(features)}] = {{{', '.join([f'{x:.4f}' for x in coefs[i]])}}};\n"
            report += f"const float class_{i}_intercept = {intercepts[i]:.4f};\n"
            report += "```\n\n"
        report += "## Edge Inference Strategy\n"
        report += "1. Collect features from sensors.\n"
        report += "2. Scale features: `(x - mean) / scale`.\n"
        report += "3. Compute dot product for each class: `sum(scaled_x * weights) + intercept`.\n"
        report += "4. Apply softmax to get probabilities.\n"
    else:
        report += "## Edge Inference Strategy\n"
        report += "Since the selected model is not linear (e.g. Random Forest), we recommend converting the `.pkl` using tools like `emlearn` or `m2cgen` to generate C code directly, or using TensorFlow Lite Micro if retraining as a neural network.\n"
        
    with open(os.path.join(reports_dir, "heat_edge_deployment_report.md"), "w") as f:
        f.write(report)
        
    print("Edge deployment config generated.")

if __name__ == "__main__":
    main()
