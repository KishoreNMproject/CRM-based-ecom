from fastapi import FastAPI
import pandas as pd
from rfm_model import get_rfm_clusters
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "/data/online_retail.csv"
df = pd.read_csv(DATA_FILE)

@app.get("/")
def home():
    return {"message": "Shopping Analytics API running"}

@app.get("/api/rfm")
def rfm_analysis():
    rfm_data = get_rfm_clusters(df)
    return rfm_data.to_dict(orient="records")