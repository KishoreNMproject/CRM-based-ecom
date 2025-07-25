
from fastapi import APIRouter, Request
import csv
import os

router = APIRouter(prefix="/analytics", tags=["Analytics"])

DATA_FILE = "data/analytics_data.csv"
os.makedirs("data", exist_ok=True)

@router.post("/log")
async def log_event(request: Request):
    data = await request.json()
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "timestamp", "event", "product"])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
    return {"status": "logged"}

@router.get("/data")
def get_data():
    with open(DATA_FILE, "r") as f:
        return f.read()
