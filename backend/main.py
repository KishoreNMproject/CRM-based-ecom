from fastapi import FastAPI
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime
import uvicorn

app = FastAPI()

# Load dataset
data = pd.read_csv("data/online_retail.csv")

# Clean data
data = data.dropna(subset=['Customer ID'])
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['TotalPrice'] = data['Quantity'] * data['Price']

# RFM calculation
def get_rfm():
    NOW = datetime(2011, 12, 10)
    rfm = data.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (NOW - x.max()).days,
        'Invoice': 'count',
        'TotalPrice': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalPrice': 'Monetary'})
    return rfm

@app.get("/rfm")
def rfm_data():
    return get_rfm().reset_index().to_dict(orient='records')

@app.get("/clusters")
def clusters():
    rfm = get_rfm()
    kmeans = KMeans(n_clusters=4, random_state=42)
    rfm['Cluster'] = kmeans.fit_predict(rfm[['Recency', 'Frequency', 'Monetary']])
    return rfm.reset_index().to_dict(orient='records')

@app.get("/top_products")
def top_products():
    top_products = data.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
    return top_products.reset_index().to_dict(orient='records')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
