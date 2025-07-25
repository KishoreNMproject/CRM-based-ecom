import shap
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def explain_shap(df):
    df = df.dropna()
    model = RandomForestClassifier().fit(df.iloc[:, :-1], df.iloc[:, -1])
    explainer = shap.Explainer(model)
    shap_values = explainer(df.iloc[:, :-1])
    return {"shap_summary": shap_values.data.tolist()}

def explain_lime(df, customer_id):
    return {"lime_explanation": f"LIME output for customer {customer_id}"}
