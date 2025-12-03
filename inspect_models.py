import pickle
import pandas as pd
import os

model_dir = "models"

def inspect_pickle(filename):
    path = os.path.join(model_dir, filename)
    if os.path.exists(path):
        print(f"--- {filename} ---")
        try:
            data = pickle.load(open(path, "rb"))
            print(data)
            if isinstance(data, list):
                print("List length:", len(data))
            if hasattr(data, 'classes_'):
                print("Classes:", data.classes_)
            if isinstance(data, dict):
                print("Keys:", data.keys())
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    else:
        print(f"File not found: {filename}")

inspect_pickle("regression_features_clean.pkl")
inspect_pickle("label_encoders.pkl")
