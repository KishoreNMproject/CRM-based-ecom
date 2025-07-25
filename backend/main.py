from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import shap
import joblib
import numpy as np

from utils import (
    load_data,
    calculate_rfm,
    explain_shap,
    explain_lime,
    get_customer_profile,
    get_business_rules,
)

app = FastAPI()

# Load dataset
df = load_data("data/online_retail.csv")
rfm_df = calculate_rfm(df)

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
