# backend/explainer.py

import pandas as pd
from utils import explain_shap, explain_lime, get_business_rules, load_dataset

# Shared dataset path — adjust if you're using a different file
DEFAULT_DATASET_PATH = "data/online_retail.csv"

def fetch_dataset(path: str = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    df = load_dataset(path)
    if df.empty:
        raise ValueError("Dataset is empty or not found.")
    return df

def get_shap_results(target_column: str = "Country", path: str = DEFAULT_DATASET_PATH):
    try:
        df = fetch_dataset(path)
        result = explain_shap(df, target_column)
        return {
            "status": "success",
            "type": "shap",
            "target": target_column,
            "feature_names": result.get("feature_names", []),
            "mean_abs_shap_values": result.get("mean_abs_shap_values", [])
        }
    except Exception as e:
        return {
            "status": "error",
            "type": "shap",
            "message": str(e)
        }

def get_lime_results(target_column: str = "Country", path: str = DEFAULT_DATASET_PATH):
    try:
        df = fetch_dataset(path)
        result = explain_lime(df, target_column)
        return {
            "status": "success",
            "type": "lime",
            "target": target_column,
            "lime_explanation": result
        }
    except Exception as e:
        return {
            "status": "error",
            "type": "lime",
            "message": str(e)
        }

def get_rule_insights(path: str = "rfm_output.csv"):
    try:
        rfm_df = pd.read_csv(path)
        rules = get_business_rules(rfm_df)
        return {
            "status": "success",
            "type": "rules",
            "rules": rules
        }
    except Exception as e:
        return {
            "status": "error",
            "type": "rules",
            "message": str(e)
        }
