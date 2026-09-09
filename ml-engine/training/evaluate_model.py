# evaluate_model.py — owner: Kousic
import pandas as pd
import joblib
import os
import json

def generate_evaluation_report():
    print("Initiating Hybrid Model Evaluation...\n")

    #Robust pathing to find the model and data safely
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Assuming this file is in ml-engine/training/
    model_path = os.path.join(current_dir, "..", "models", "model.pkl")
    if not os.path.exists(model_path):
        # Fallback just in case it's in the root folder
        model_path = os.path.join(current_dir, "models", "model.pkl")
        
    data_path = os.path.join(current_dir, "..", "..", "data-pipeline", "processed_data", "projects_clean.csv")
    if not os.path.exists(data_path):
        data_path = "projects_clean.csv"

    #Load the Engine
    try:
        engine = joblib.load(model_path)
    except FileNotFoundError:
        print(f"[ERROR] Missing model file at {model_path}. Run train_model.py first.")
        return

    #Load the Data
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"[ERROR] Missing dataset at {data_path}.")
        return
    
    #Replicate the exact 4-feature engineering used in training
    features = df[['sanctioned_amount', 'expenditure', 'progress_percent']].copy()
    features['progress_percent'] = features['progress_percent'].fillna(0)
    features['burn_rate'] = features['expenditure'] / (features['progress_percent'] + 1.0)

    #Run AI Predictions
    predictions = engine.predict(features)
    risk_scores = engine.decision_function(features) 

    #Calculate Hackathon Metrics
    total_projects = len(features)
    anomalies = list(predictions).count(-1)
    flag_rate = (anomalies / total_projects) * 100
    
    verdict = "PASS" if 2.0 <= flag_rate <= 10.0 else "WARNING: Check False Positives/Negatives"

    print("=== HYBRID ML ENGINE: EVALUATION REPORT ===")
    print(f"Total Projects Analyzed : {total_projects}")
    print(f"Total Anomalies Flagged : {anomalies}")
    print(f"Overall Flag Rate       : {flag_rate:.2f}%")
    print(f"Average AI Risk Score   : {risk_scores.mean():.4f}")
    print(f"\n[VERDICT] {verdict}")

    #Generate JSON for Frontend's Dashboard
    report_data = {
        "metadata": {
            "project": "MPLADS Hybrid Engine",
            "model_type": "4D Isolation Forest + Rule-Based",
            "contamination_parameter": 0.05
        },
        "metrics": {
            "total_projects_analyzed": total_projects,
            "total_anomalies_flagged": anomalies,
            "overall_flag_rate_percent": round(flag_rate, 2),
            "average_ai_risk_score": round(float(risk_scores.mean()), 4)
        },
        "verdict": verdict
    }

    # Save the JSON right next to the model.pkl file
    json_path = os.path.join(os.path.dirname(model_path), "evaluation_report.json")
    with open(json_path, "w") as json_file:
        json.dump(report_data, json_file, indent=4)
        
    print(f"\n[SUCCESS] JSON report generated at: {os.path.abspath(json_path)}")

if __name__ == "__main__":
    generate_evaluation_report()