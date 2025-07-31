from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import (
    load_features_from_csv,
    train_kmeans_with_elbow,
    save_model,
    load_model,
    save_train_status,
    load_train_status
)
import os

app = FastAPI()

# Enable CORS for browser extension/app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, set specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Customer Behavior Model Trainer API Ready."}

@app.post("/train")
def train_model():
    try:
        data = load_features_from_csv("full_customer_features.csv")
        if data.empty:
            raise HTTPException(status_code=400, detail="CSV is empty or not found.")

        model, n_clusters = train_kmeans_with_elbow(data)
        save_model(model, "model.pkl")
        save_train_status(n_clusters=n_clusters, data_points=len(data))
        return {"status": "success", "clusters": n_clusters, "data_points": len(data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    try:
        status = load_train_status()
        return status or {"status": "no training yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))