from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# CORS settings for frontend communication (React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to CSV
DATA_FILE = os.path.join("data", "online_retail.csv")

# Load dataset once (optional for simplicity)
@app.on_event("startup")
def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Dataset not found at {DATA_FILE}")
    global df
    df = pd.read_csv(DATA_FILE, encoding='ISO-8859-1')
    df.dropna(subset=["Customer ID", "Description", "Invoice"], inplace=True)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

@app.get("/")
def root():
    return {"message": "Shopping Analytics API is live"}

@app.get("/summary")
def get_summary():
    if df is None:
        return {"error": "Data not loaded"}
    top_products = df['Description'].value_counts().head(10).to_dict()
    return {"top_products": top_products}

# Additional endpoints can be added below
