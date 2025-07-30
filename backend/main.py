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

    os.makedirs("data", exist_ok=True)
    rfm_df.to_csv("data/rfm_output.csv", index=False)

except Exception as e:
    raise RuntimeError(f"Startup failed: {e}")


@app.get("/")
def root():
    return {"message": "Shopping Analytics API is live"}


# ✅ Chart-friendly RFM data
@app.get("/rfm")
def get_rfm_chart():
    try:
        segment_counts = rfm_df["Segment"].value_counts()
        return {
            "labels": segment_counts.index.tolist(),
            "values": segment_counts.values.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🧪 Optional: full RFM table
@app.get("/rfm/full")
def get_rfm_table():
    return rfm_df.to_dict(orient="records")


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    try:
        return get_customer_profile(df, customer_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Customer ID not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Chart-friendly SHAP output
@app.get("/shap")
def shap_explanation():
    try:
        shap_result = explain_shap(df, target_column="Cluster")
        if isinstance(shap_result, dict):
            return {
                "labels": list(shap_result.keys()),
                "values": list(shap_result.values())
            }
        else:
            return shap_result  # fallback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Chart-friendly LIME for customer
@app.get("/lime")
def lime_explanation(customer_id: str = Query(..., description="Customer ID to explain using LIME")):
    try:
        lime_result = explain_lime(df, customer_id)
        if isinstance(lime_result, dict):
            return {
                "labels": list(lime_result.keys()),
                "values": list(lime_result.values())
            }
        else:
            return lime_result
    except KeyError:
        raise HTTPException(status_code=404, detail="Customer ID not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Chart-friendly Business Rules
@app.get("/rules")
def rules():
    try:
        rfm_csv_path = "data/rfm_output.csv"
        rfm_loaded_df = pd.read_csv(rfm_csv_path)
        rules_result = get_business_rules(rfm_loaded_df)

        if isinstance(rules_result, dict):
            return {
                "labels": list(rules_result.keys()),
                "values": list(rules_result.values())
            }
        else:
            return rules_result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Required file '{rfm_csv_path}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
