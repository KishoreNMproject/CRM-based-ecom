import pandas as pd
import json
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import numpy as np
import shap
import lime
import lime.lime_tabular


def load_features_from_csv(path="full_customer_features.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def train_kmeans_with_elbow(data, max_k=10):
    features = data.select_dtypes(include=['number'])
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    sse = []
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled)
        sse.append(kmeans.inertia_)

    # Elbow point detection
    diffs = [sse[i] - sse[i + 1] for i in range(len(sse) - 1)]
    elbow_k = next((i + 2 for i, diff in enumerate(diffs) if diff < 0.1 * diffs[0]), 3)

    final_model = KMeans(n_clusters=elbow_k, random_state=42, n_init=10)
    final_model.fit(scaled)
    return final_model, elbow_k

def save_model(model, path="model.csv"):
    joblib.dump(model, path)

def load_model(path="model.csv"):
    return joblib.load(path)

def save_train_status(n_clusters, data_points, path="train_status.json"):
    status = {
        "trained_at": datetime.now().isoformat(),
        "clusters": n_clusters,
        "data_points": data_points
    }
    with open(path, "w") as f:
        json.dump(status, f, indent=2)

def load_train_status(path="train_status.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def calculate_rfm():
    df = pd.read_pickle("full_customer_features.csv")
    model = joblib.load("model.csv")  # RFM clustering model (KMeans)

    features = df[['recency', 'frequency', 'monetary']]
    scaler = joblib.load("scaler.csv")
    scaled = scaler.transform(features)

    labels = model.predict(scaled)
    cluster_counts = pd.Series(labels).value_counts().sort_index().to_dict()
    return {f"Cluster {k}": int(v) for k, v in cluster_counts.items()}

def explain_shap():
    df = pd.read_pickle("full_customer_features.csv")
    model = joblib.load("model.csv")
    scaler = joblib.load("scaler.csv")

    X = scaler.transform(df[['recency', 'frequency', 'monetary']])
    explainer = shap.KernelExplainer(model.predict, X[:100])
    shap_values = explainer.shap_values(X[:1])

    feature_names = ['recency', 'frequency', 'monetary']
    shap_summary = dict(zip(feature_names, map(float, shap_values[0])))
    return shap_summary

def explain_lime():
    df = pd.read_pickle("full_customer_features.csv")
    model = joblib.load("model.csv")
    scaler = joblib.load("scaler.csv")

    features = ['recency', 'frequency', 'monetary']
    X = df[features]
    scaled_X = scaler.transform(X)

    explainer = lime.lime_tabular.LimeTabularExplainer(
        scaled_X, feature_names=features, verbose=False, mode='classification'
    )

    explanation = explainer.explain_instance(scaled_X[0], model.predict, num_features=3)
    return dict(explanation.as_list())

def get_business_rules():
    df = pd.read_pickle("full_customer_features.csv")
    rules = {
        "High Value": df[df['monetary'] > df['monetary'].quantile(0.75)].shape[0],
        "At Risk": df[df['recency'] > df['recency'].quantile(0.75)].shape[0],
        "Churned": df[(df['frequency'] < 2) & (df['recency'] > df['recency'].median())].shape[0],
        "New Customers": df[df['tenure'] < 30].shape[0] if 'tenure' in df.columns else 0
    }
    return rules