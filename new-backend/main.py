from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from datetime import datetime

app = FastAPI()

# Paths
DATA_FILE = "full_customer_features.pkl"
MODEL_FILE = "kmeans_model.pkl"
SCALER_FILE = "scaler.pkl"
STATUS_FILE = "training_status.json"

# Templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# HTML Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route: Train the model
@app.get("/train")
def train_model():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_pickle(DATA_FILE)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    inertias = []
    for k in range(2, 10):
        model = KMeans(n_clusters=k, n_init=10, random_state=42)
        model.fit(X_scaled)
        inertias.append(model.inertia_)

    diff = np.diff(inertias)
    k_opt = diff.argmin() + 2

    model = KMeans(n_clusters=k_opt, n_init=10, random_state=42)
    model.fit(X_scaled)

    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    with open(STATUS_FILE, "w") as f:
        json.dump({
            "trained_at": str(datetime.now()),
            "n_clusters": k_opt,
            "data_points": len(df)
        }, f)

    return {"message": "✅ Model trained", "clusters": k_opt}

# Route: Check training status
@app.get("/status")
def status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"message": "Model not trained yet"}

# Route: Predict with JSON payload
class InputFeatures(BaseModel):
    features: List[float]

@app.post("/predict")
def predict(input: InputFeatures):
    if not os.path.exists(MODEL_FILE):
        raise HTTPException(status_code=400, detail="Train the model first")
    
    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)

    input_scaled = scaler.transform([input.features])
    cluster = model.predict(input_scaled)[0]

    return {"cluster": int(cluster)}

# HTML interface to test prediction from form
@app.post("/predict_form", response_class=HTMLResponse)
async def predict_form(request: Request, feature_input: str = Form(...)):
    features = [float(x.strip()) for x in feature_input.split(",")]

    if not os.path.exists(MODEL_FILE):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "prediction_result": "❌ Train the model first."
        })

    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)
    pred = model.predict(scaler.transform([features]))[0]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction_result": f"Predicted Cluster: {pred}"
    })
