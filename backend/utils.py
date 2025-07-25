import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import shap
import lime
import lime.lime_tabular
from baconpy import Bacon
import joblib

def load_data(path):
    df = pd.read_csv(path)
    df.dropna(subset=['Customer ID'], inplace=True)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

def calculate_rfm(df):
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'count',
        'Price': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    return rfm

def get_customer_profile(df, customer_id):
    customer_data = df[df['Customer ID'] == float(customer_id)]
    return {
        "CustomerID": customer_id,
        "Purchases": len(customer_data),
        "TotalSpent": round(customer_data['Price'].sum(), 2),
        "RecentPurchase": str(customer_data['InvoiceDate'].max()),
        "TopProducts": customer_data['Description'].value_counts().head(5).to_dict()
    }

def explain_shap(df):
    rfm = calculate_rfm(df).drop(columns=["CustomerID"])
    model = KMeans(n_clusters=4, random_state=42).fit(rfm)
    explainer = shap.Explainer(model.predict, rfm)
    shap_values = explainer(rfm)
    top_features = np.mean(np.abs(shap_values.values), axis=0)
    return dict(zip(rfm.columns, top_features.round(2).tolist()))

def explain_lime(df, customer_id):
    rfm = calculate_rfm(df)
    customer_index = rfm[rfm["CustomerID"] == float(customer_id)].index[0]
    features = rfm.drop(columns=["CustomerID"])
    model = KMeans(n_clusters=4, random_state=42).fit(features)
    explainer = lime.lime_tabular.LimeTabularExplainer(
        features.values, feature_names=features.columns, class_names=["Cluster 0", "Cluster 1", "Cluster 2", "Cluster 3"],
        mode="classification"
    )
    exp = explainer.explain_instance(features.values[customer_index], model.predict)
    return dict(exp.as_list())

def get_business_rules(rfm):
    bacon = Bacon()
    rules = bacon.learn(rfm[['Recency', 'Frequency', 'Monetary']])
    readable_rules = [str(r) for r in rules]
    return {"rules": readable_rules}
