import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

def train_hybrid_engine():
    print("Initializing Hybrid MPLADS ML Engine...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "..", "data-pipeline", "processed_data", "projects_clean.csv")
    
    if not os.path.exists(data_path):
        data_path = "projects_clean.csv"
        
    df = pd.read_csv(data_path)
    
    print("\nEngineering Real-World Fraud Metrics...")
    
    # 1. We strictly define the 3 base features
    features = df[['sanctioned_amount', 'expenditure', 'progress_percent']].copy()
    features['progress_percent'] = features['progress_percent'].fillna(0)
    
    # 2. We engineer the 4th feature (burn_rate)
    features['burn_rate'] = features['expenditure'] / (features['progress_percent'] + 1)
    
    # 3. Print the columns to the terminal so we can visually verify it sees all 4
    print(f"Training on exactly these columns: {list(features.columns)}")
    
    print("Training 4-Dimensional Isolation Forest...")
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_forest.fit(features)
    
    # 4. Save directly to the models directory
    models_dir = os.path.join(current_dir, "..", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "model.pkl")
    joblib.dump(iso_forest, model_path)
    
    print(f"\n[SUCCESS] Hybrid Engine compiled and saved to: {os.path.abspath(model_path)}")

if __name__ == "__main__":
    train_hybrid_engine()