from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import numpy as np
import os

app = FastAPI()

# Load dataset (CSV or PKL)
DATA_PATH = "full_customer_features.pkl"
MODEL_PATH = "kmeans_model.pkl"
SCALER_PATH = "scaler.pkl"

def load_data():
    if os.path.exists(DATA_PATH):
        if DATA_PATH.endswith(".pkl"):
            return pd.read_pickle(DATA_PATH)
        elif DATA_PATH.endswith(".csv"):
            return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

def find_best_k(data):
    distortions = []
    K_range = range(2, 11)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(data)
        distortions.append(kmeans.inertia_)
    # Use the elbow method manually or use silhouette score
    best_k = 3
    best_score = -1
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k

@app.post("/train")
def train_model():
    df = load_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not found or empty")

    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df.values)

    # Find best k using silhouette method
    best_k = find_best_k(X_scaled)

    # Train KMeans
    kmeans = KMeans(n_clusters=best_k, random_state=42)
    kmeans.fit(X_scaled)

    # Save model and scaler
    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "status": "trained",
        "clusters": best_k,
        "inertia": kmeans.inertia_,
        "samples": len(df)
    }

class PredictRequest(BaseModel):
    features: list[list[float]]  # 2D List

@app.post("/predict")
def predict(req: PredictRequest):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise HTTPException(status_code=400, detail="Model not trained yet")
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import numpy as np
import os

app = FastAPI()

# Load dataset (CSV or PKL)
DATA_PATH = "full_customer_features.pkl"
MODEL_PATH = "kmeans_model.pkl"
SCALER_PATH = "scaler.pkl"

def load_data():
    if os.path.exists(DATA_PATH):
        if DATA_PATH.endswith(".pkl"):
            return pd.read_pickle(DATA_PATH)
        elif DATA_PATH.endswith(".csv"):
            return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

def find_best_k(data):
    distortions = []
    K_range = range(2, 11)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(data)
        distortions.append(kmeans.inertia_)
    # Use the elbow method manually or use silhouette score
    best_k = 3
    best_score = -1
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k

@app.post("/train")
def train_model():
    df = load_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not found or empty")

    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df.values)

    # Find best k using silhouette method
    best_k = find_best_k(X_scaled)

    # Train KMeans
    kmeans = KMeans(n_clusters=best_k, random_state=42)
    kmeans.fit(X_scaled)

    # Save model and scaler
    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "status": "trained",
        "clusters": best_k,
        "inertia": kmeans.inertia_,
        "samples": len(df)
    }

class PredictRequest(BaseModel):
    features: list[list[float]]  # 2D List

@app.post("/predict")
def predict(req: PredictRequest):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise HTTPException(status_code=400, detail="Model not trained yet")

    kmeans = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    X = np.array(req.features)
    X_scaled = scaler.transform(X)
    preds = kmeans.predict(X_scaled)

    return {"labels": preds.tolist()}

@app.get("/status")
def status():
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        return {
            "trained": True,
            "n_clusters": model.n_clusters,
            "inertia": model.inertia_
        }
    return {"trained": False}

    kmeans = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    X = np.array(req.features)
    X_scaled = scaler.transform(X)
    preds = kmeans.predict(X_scaled)

    return {"labels": preds.tolist()}

@app.get("/status")
def status():
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        return {
            "trained": True,
            "n_clusters": model.n_clusters,
            "inertia": model.inertia_
        }
    return {"trained": False}
