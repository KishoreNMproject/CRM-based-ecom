# main.py
from fastapi import FastAPI, HTTPException, Request
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
import requests # Import the requests library for making API calls
from fastapi.responses import JSONResponse

# You will need a .env file for local development, but Render will handle this.
from dotenv import load_dotenv
load_dotenv()

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
    """Root endpoint for the API."""
    return {"message": "Customer Behavior Model Trainer API Ready."}

@app.post("/train")
def train_model():
    """Triggers the training of the K-means model and saves it."""
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
    """Retrieves the status of the last model training run."""
    try:
        status = load_train_status()
        return status or {"status": "no training yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import Body
import httpx

@app.post("/priceapi-proxy")
async def priceapi_proxy(payload: dict):
    query = payload.get("query", "")
    country = payload.get("country", "in")

    token = os.getenv("PRICEAPI_TOKEN")
    if not token:
        return JSONResponse(content={"error": "Missing PRICEAPI_TOKEN in env"}, status_code=500)

    if not query:
        return JSONResponse(content={"error": "Missing query"}, status_code=400)

    priceapi_url = "https://api.priceapi.com/v2/jobs"
    data = {
        "token": token,
        "country": country,
        "source": "amazon",
        "topic": "search_results",
        "key": "term",  # ✅ 'term' is valid
        "values": query,
        "max_age": "43200",
        "location": "",
    }

    try:
        job_response = requests.post(priceapi_url, data=data)
        job_data = job_response.json()
        print("🔍 PriceAPI Job Response:", job_data)

        job_id = job_data.get("job_id")
        if not job_id:
            return JSONResponse(content={"error": "Failed to fetch job ID from PriceAPI", "details": job_data}, status_code=500)

        import time
        result_url = f"https://api.priceapi.com/v2/jobs/{job_id}/download.json"

        for _ in range(20):
            result_response = requests.get(result_url, params={"token": token})
            result_data = result_response.json()
            status = result_data.get("status", "unknown")  # ✅ Define it

            print("⏳ Polling Result:", result_data)

            
            if status == "finished":
                results = result_data.get("results", [])
                if not results or not results[0].get("success", True):
                    return JSONResponse(
                        content={"error": "PriceAPI returned no results", "details": results},
                        status_code=500
                )
                return result_data

            elif status in {"working", "new"}:
                time.sleep(1)
            else:
                return JSONResponse(
                    content={"error": "Unexpected job status", "details": result_data},
                    status_code=500
                )

        return JSONResponse(content={"error": "Job timed out. Try again later."}, status_code=504)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
import pandas as pd

# Load customer features at startup
customer_df = pd.read_csv("full_customer_features.csv")

@app.post("/assign-cluster")
def assign_cluster(customer_id: int = Body(..., embed=True)):
    """
    Assigns a cluster to a customer based on existing features.
    Returns features and pseudo-cluster group (e.g., Low/Medium/High value)
    """
    customer = customer_df[customer_df["CustomerID"] == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer ID not found.")

    record = customer.iloc[0].to_dict()

    # Simple placeholder clustering logic (can be replaced with real model)
    if record["Monetary"] > 5000:
        cluster = "High Value"
    elif record["Monetary"] > 2000:
        cluster = "Medium Value"
    else:
        cluster = "Low Value"

    return {"customer_id": customer_id, "cluster": cluster, "features": record}


@app.post("/log-activity")
def log_customer_activity(customer_id: int = Body(...), action: str = Body(...), product: str = Body(...)):
    """
    Logs a customer's action for analytics.
    """
    import datetime
    log_entry = {
        "customer_id": customer_id,
        "action": action,
        "product": product,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    with open("customer_activity_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return {"status": "logged"}


@app.get("/analytics-data")
def get_analytics_data():
    """
    Prepares data for RFM, SHAP, LIME, and business rules dashboards.
    """
    return customer_df.to_dict(orient="records")
