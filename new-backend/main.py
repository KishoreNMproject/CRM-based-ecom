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
from utils import calculate_rfm, explain_shap, explain_lime, get_business_rules

# You will need a .env file for local development, but Render will handle this.
# from dotenv import load_dotenv
# load_dotenv()

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

@app.get("/rfm")
def get_rfm():
    return calculate_rfm()

@app.get("/shap")
def get_shap():
    return explain_shap()

@app.get("/lime")
def get_lime():
    return explain_lime()

@app.get("/rules")
def get_rules():
    return get_business_rules()


@app.post("/gemini-proxy")
async def gemini_proxy(request: Request):
    """
    A secure proxy endpoint to call the Gemini API.
    The Gemini API key is retrieved from environment variables.
    """
    # Retrieve the API key from environment variables
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured on backend.")

    try:
        data = await request.json()
        query = data.get('query', 'general online deals')
        source_url = data.get('sourceUrl', 'N/A')

        # Construct the prompt for Gemini
        prompt = f"""Given the search term "{query}", provide general advice or insights on finding good deals across various e-commerce sites like Amazon, Flipkart, eBay, Newegg, and Best Buy. 
        Suggest common strategies or types of products that often have good discounts for this category.
        Keep the response concise and actionable."""
        
        # Define the Gemini API call payload
        gemini_payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Make the actual server-to-server call to the Gemini API
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
        
        gemini_response = requests.post(gemini_api_url, json=gemini_payload)
        gemini_response.raise_for_status()  # Raise an exception for HTTP errors

        # Relay the response back to the extension
        return gemini_response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to get response from Gemini API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")