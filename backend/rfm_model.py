import pandas as pd
from sklearn.cluster import KMeans
# rfm_model.py

import pandas as pd
from sklearn.cluster import KMeans

def get_rfm_clusters(df):
    # Validate required columns
    required_cols = ['Customer ID', 'InvoiceDate', 'Invoice', 'Quantity', 'Price']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in dataset: {missing_cols}")

    df = df.copy()
    df['TotalPrice'] = df['Quantity'] * df['Price']

    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (pd.to_datetime('now') - pd.to_datetime(x.max())).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()

    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    # Optional: remove negative or zero monetary (if any bad data)
    rfm = rfm[(rfm['Monetary'] > 0) & (rfm['Frequency'] > 0)]

    # KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    rfm['Cluster'] = kmeans.fit_predict(rfm[['Recency', 'Frequency', 'Monetary']])

    return rfm

def get_rfm_clusters(df):
    df['TotalPrice'] = df['Quantity'] * df['Price']
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (pd.to_datetime('now') - pd.to_datetime(x.max())).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    kmeans = KMeans(n_clusters=4, random_state=42)
    rfm['Cluster'] = kmeans.fit_predict(rfm[['Recency', 'Frequency', 'Monetary']])
    return rfm