# main.py

from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import os

from utils import load_dataset, get_customer_profile
from explainers import explain_shap, explain_lime
from rules import get_business_rules
from rfm_model import get_rfm_clusters

app = FastAPI(title="Shopping Analytics API")

# Load dataset and generate RFM DataFrame
try:
    df = load_dataset("data/online_retail.csv")
    rfm_df = get_rfm_clusters(df)

    # Ensure data directory exists and save RFM output CSV
    os.makedirs("data", exist_ok=True)
    rfm_df.to_csv("data/rfm_output.csv", index=False)

except Exception as e:
    raise RuntimeError(f"Startup failed: {e}")


@app.get("/")
def root():
    return {"message": "Shopping Analytics API is live"}


@app.get("/rfm")
def get_rfm():
    return rfm_df.to_dict(orient="records")


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    try:
        return get_customer_profile(df, customer_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Customer ID not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/shap")
def shap_explanation():
    try:
        return explain_shap(df, target_column="Cluster")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lime")
def lime_explanation(customer_id: str = Query(..., description="Customer ID to explain using LIME")):
    try:
        return explain_lime(df, customer_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Customer ID not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rules")
def rules():
    try:
        rfm_csv_path = "data/rfm_output.csv"
        rfm_loaded_df = pd.read_csv(rfm_csv_path)
        return get_business_rules(rfm_loaded_df)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Required file '{rfm_csv_path}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
