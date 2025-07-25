from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import shap
import joblib
import numpy as np

from utils import (
    load_dataset,
    get_customer_profile
)

from explainers import explain_shap, explain_lime
from rules import get_business_rules
from rfm_model import get_rfm_clusters

from rfm_model import get_rfm_clusters

app = FastAPI()

# Load dataset
df = load_dataset("data/online_retail.csv")
rfm_df = get_rfm_clusters(df)


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

@app.get("/shap")
def shap_explanation():
    return explain_shap(df)

@app.get("/lime")
def lime_explanation(customer_id: str):
    return explain_lime(df, customer_id)

@app.get("/rules")
def business_rules():
    return get_business_rules(rfm_df)
