import shap
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


def explain_shap(df, sample_size=100):
    # Drop NaNs and sample to reduce memory usage
    df = df.dropna()
    if sample_size and len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)

    # Use TreeExplainer with low-memory default settings
    explainer = shap.TreeExplainer(model, feature_perturbation="tree_path_dependent")
    shap_values = explainer.shap_values(X, approximate=True)

    # Summarize feature importances (mean absolute value)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    # Return minimal JSON-friendly output
    return {
        "features": list(X.columns),
        "mean_abs_shap": mean_abs_shap.tolist()
    }
def explain_lime(df, customer_id):
    return {"lime_explanation": f"LIME output for customer {customer_id}"}
