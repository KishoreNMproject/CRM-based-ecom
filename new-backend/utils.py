import pandas as pd
import json
import joblib
from datetime import datetime
import numpy as np

# Dummy replacements
def load_features_from_csv(path="full_customer_features.csv"):
    return pd.DataFrame({
        'recency': [10, 20, 30],
        'frequency': [1, 3, 2],
        'monetary': [100, 200, 150]
    })

def train_kmeans_with_elbow(data, max_k=10):
    class DummyModel:
        def predict(self, X): return [0] * len(X)
        def fit(self, X): pass
    return DummyModel(), 3

def save_model(model, path="model.pkl"):
    pass  # Dummy no-op

def load_model(path="model.pkl"):
    class DummyModel:
        def predict(self, X): return [0] * len(X)
    return DummyModel()

def save_train_status(n_clusters, data_points, path="train_status.json"):
    status = {
        "trained_at": datetime.now().isoformat(),
        "clusters": n_clusters,
        "data_points": data_points
    }
    with open(path, "w") as f:
        json.dump(status, f, indent=2)

def load_train_status(path="train_status.json"):
    return {"trained_at": "2025-01-01T00:00:00", "clusters": 3, "data_points": 100}

def calculate_rfm():
    return {
        "Cluster 0": 50,
        "Cluster 1": 30,
        "Cluster 2": 20
    }

def explain_shap():
    return {
        "recency": -0.1,
        "frequency": 0.2,
        "monetary": 0.5
    }

def explain_lime():
    return {
        "monetary > 100": 0.4,
        "recency <= 20": 0.3,
        "frequency == 2": 0.3
    }

def get_business_rules():
    return {
        "High Value": 25,
        "At Risk": 10,
        "Churned": 5,
        "New Customers": 8
    }
