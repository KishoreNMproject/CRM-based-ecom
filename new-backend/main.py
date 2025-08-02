# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from utils import (
    load_features_from_csv,
    train_kmeans_with_elbow,
    save_model,
    load_model,
    save_train_status,
    load_train_status
)
import os
import requests # Import the requests library for making API calls
from fastapi.responses import JSONResponse
import json
from selenium import webdriver
import time

app = FastAPI()

# Enable CORS for browser extension/app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, set specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint for the API."""
    return {"message": "Customer Behavior Model Trainer API Ready."}

@app.post("/train")
def train_model():
    """Triggers the training of the K-means model and saves it."""
    try:
        data = load_features_from_csv("full_customer_features.csv")
        if data.empty:
            raise HTTPException(status_code=400, detail="CSV is empty or not found.")

        model, n_clusters = train_kmeans_with_elbow(data)
        save_model(model, "model.pkl")
        save_train_status(n_clusters=n_clusters, data_points=len(data))
        return {"status": "success", "clusters": n_clusters, "data_points": len(data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    """Retrieves the status of the last model training run."""
    try:
        status = load_train_status()
        return status or {"status": "no training yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import Body


@app.post("/priceapi-proxy")
async def priceapi_proxy(payload: dict):
    query = payload.get("query", "")
    country = payload.get("country", "in")

    driver = webdriver.Chrome()  # Use Chrome browser for scraping

    driver.get(f"https://www.amazon.com/s?k={query}&ref=nb_sb_noss_2&url=search-alias{country}")
    time.sleep(5)  # Wait for page to load

    search_results = []

    for item in driver.find_elements_by_xpath('//div[@class="a-section aok-relative s-result-item celwidget"]'):
        title = item.find_element_by_xpath('.//h2[@class="a-size-medium product-title a-text-normal"]').text
        price = item.find_element_by_xpath('.//span[@id="priceblock_ourprice"]/span[@class="a-price"]').text
        rating = item.find_element_by_xpath('.//span[@class="a-icon-alt a-star-4-5"]').get_attribute("aria-labeledby")

        search_results.append({
            "title": title,
            "price": price,
            "rating": rating
        })

    driver.quit()  # Close the browser after scraping is done

    return JSONResponse(content=search_results)

@app.post("/navigate")
async def navigate(request: Request):
    data = await request.json()
    action, url = data["action"], data["url"]

    if action == "navigate":
        await navigation(url)
    return {"status": "success"}

def navigation(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)  # Wait for page to load


@app.post("/assign-cluster")
def assign_cluster(customer_id: int = Body(..., embed=True)):
    """
    Assigns a cluster to a customer based on existing features.
    Returns features and pseudo-cluster group (e.g., Low/Medium/High value)
    """
    customer = customer_df[customer_df["CustomerID"] == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer ID not found.")

    record = customer.iloc[0].to_dict()

    # Simple placeholder clustering logic (can be replaced with real model)
    if record["Monetary"] > 5000:
        cluster = "High Value"
    elif record["Monetary"] > 2000:
        cluster = "Medium Value"
    else:
        cluster = "Low Value"

    return {"customer_id": customer_id, "cluster": cluster, "features": record}


@app.post("/log-activity")
def log_customer_activity(customer_id: int = Body(...), action: str = Body(...), product: str = Body(...)):
    """
    Logs a customer's action for analytics.
    """
    import datetime
    log_entry = {
        "customer_id": customer_id,
        "action": action,
        "product": product,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    with open("customer_activity_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return {"status": "logged"}


@app.get("/analytics-data")
def get_analytics_data():
    """
    Prepares data for RFM, SHAP, LIME, and business rules dashboards.
    """
    return customer_df.to_dict(orient="records")
