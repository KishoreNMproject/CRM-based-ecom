import platform
import psutil
import uuid
import socket
import hashlib
import pandas as pd
import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap
import lime
import lime.lime_tabular

def get_machine_info():
    try:
        total_ram_gb = psutil.virtual_memory().total / (1024.0 ** 3)
        return {
            "platform": platform.system(),
            "platform-release": platform.release(),
            "platform-version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "ip-address": socket.gethostbyname(socket.gethostname()),
            "mac-address": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                     for ele in range(0,8*6,8)][::-1]),
            "processor": platform.processor(),
            "ram": f"{round(total_ram_gb)} GB"
        }
    except Exception as e:
        return {"error": str(e)}

def generate_hash_for_machine():
    info = get_machine_info()
    raw = ''.join([str(v) for v in info.values() if v])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def load_dataset(path="data/online_retail.csv"):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_dataset(df, csv_path):
    df.to_csv(csv_path, index=False)

def get_customer_profile(df, customer_id):
    try:
        customer_id = int(customer_id)
    except ValueError:
        return {"error": "Invalid customer ID format"}

    customer_data = df[df['Customer ID'] == customer_id]

    if customer_data.empty:
        return {"error": "Customer ID not found"}

    summary = {
        "Customer ID": customer_id,
        "Total Orders": customer_data['Invoice'].nunique(),
        "Total Spend": (customer_data['Quantity'] * customer_data['Price']).sum(),
        "Most Purchased Item": customer_data['Description'].mode().iloc[0]
    }

    return summary

def calculate_rfm(df):
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'nunique',
        'Price': 'sum'
    }).reset_index()

    rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

    kmeans = KMeans(n_clusters=4, random_state=1, n_init=10)
    rfm['Segment'] = kmeans.fit_predict(rfm_scaled)
    return rfm

def explain_shap(df, target_column, num_rows=500):
    df = df.dropna().sample(min(num_rows, len(df)), random_state=1)
    X = df.drop(columns=[target_column])
    y = df[target_column]

    if not all(np.issubdtype(dt, np.number) for dt in X.dtypes):
        X = pd.get_dummies(X)

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=1)
    model = RandomForestClassifier(n_estimators=25, max_depth=5, random_state=1)
    model.fit(X_train, y_train)

    explainer = shap.Explainer(model.predict, X_train, algorithm="permutation")
    shap_values = explainer(X_train[:50], check_additivity=False)

    try:
        summary = shap_values.values.mean(axis=0)
    except Exception:
        summary = np.mean(np.abs(shap_values.data), axis=0)

    return {
        "feature_names": list(X_train.columns),
        "mean_abs_shap_values": list(np.abs(summary))
    }

def explain_lime(df, target_column, num_features=5):
    df = df.dropna().copy()
    X = df.drop(columns=[target_column])
    y = df[target_column]

    if not all(np.issubdtype(dt, np.number) for dt in X.dtypes):
        X = pd.get_dummies(X)

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=1)
    model = RandomForestClassifier(n_estimators=25, max_depth=5, random_state=1)
    model.fit(X_train, y_train)

    explainer = lime.lime_tabular.LimeTabularExplainer(
        X_train.values,
        feature_names=X_train.columns.tolist(),
        class_names=np.unique(y_train).astype(str).tolist(),
        discretize_continuous=True
    )

    exp = explainer.explain_instance(X_train.iloc[0].values, model.predict_proba, num_features=num_features)
    explanation = dict(exp.as_list())
    return explanation

def get_business_rules(df):
    try:
        rules = []

        if 'Quantity' in df.columns:
            avg_quantity = df['Quantity'].mean()
            rules.append(f"Average purchase quantity is {avg_quantity:.2f} units.")

        if 'Price' in df.columns:
            high_value_items = df[df['Price'] > df['Price'].quantile(0.95)]
            rules.append(f"Top 5% high value items: {high_value_items['Description'].nunique()} unique items.")

        if 'Country' in df.columns:
            top_country = df['Country'].value_counts().idxmax()
            rules.append(f"Most orders come from {top_country}.")

        return {"rules": rules}
    except Exception as e:
        return {"error": str(e)}
