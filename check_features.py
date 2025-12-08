import pandas as pd
import pickle
import os

csv_path = "data/cleaned/cleaned_steam.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"Columns in {csv_path}:")
    print(df.columns.tolist())
else:
    print(f"{csv_path} not found.")

encoder_path = "models/label_encoders.pkl"
if os.path.exists(encoder_path):
    try:
        encoders = pickle.load(open(encoder_path, "rb"))
        print("\nEncoder Classes:")
        for col, encoder in encoders.items():
            print(f"{col}: {encoder.classes_[:5]} ... (Total: {len(encoder.classes_)})")
    except Exception as e:
        print(f"Error loading encoders: {e}")
