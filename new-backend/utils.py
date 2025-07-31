import pandas as pd
import json
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def load_features_from_csv(path="full_customer_features.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def train_kmeans_with_elbow(data, max_k=10):
    features = data.select_dtypes(include=['number'])
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    sse = []
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled)
        sse.append(kmeans.inertia_)

    # Elbow point detection
    diffs = [sse[i] - sse[i + 1] for i in range(len(sse) - 1)]
    elbow_k = next((i + 2 for i, diff in enumerate(diffs) if diff < 0.1 * diffs[0]), 3)

    final_model = KMeans(n_clusters=elbow_k, random_state=42, n_init=10)
    final_model.fit(scaled)
    return final_model, elbow_k

def save_model(model, path="model.pkl"):
    joblib.dump(model, path)

def load_model(path="model.pkl"):
    return joblib.load(path)

def save_train_status(n_clusters, data_points, path="train_status.json"):
    status = {
        "trained_at": datetime.now().isoformat(),
        "clusters": n_clusters,
        "data_points": data_points
    }
    with open(path, "w") as f:
        json.dump(status, f, indent=2)

def load_train_status(path="train_status.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}