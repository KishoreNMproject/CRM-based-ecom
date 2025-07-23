import pandas as pd
from sklearn.cluster import KMeans

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
