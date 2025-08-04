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
from datetime import datetime
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
        try:
            df = pd.read_csv(path, encoding="ISO-8859-1", parse_dates=["InvoiceDate"], dayfirst=True)
            df.dropna(subset=["Customer ID"], inplace=True)
            df["Customer ID"] = df["Customer ID"].astype(str)
            return df
        except Exception as e:
            print(f"Error reading dataset: {e}")
            return pd.DataFrame()
    else:
        print("Dataset not found at:", path)
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



import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_rfm_output():
    path = os.path.join(BASE_DIR, "rfm_output.csv")
    return pd.read_csv(path).to_dict(orient="records")

def load_lime_output():
    path = os.path.join(BASE_DIR, "lime.csv")
    return pd.read_csv(path).to_dict(orient="records")

def load_business_rules():
    path = os.path.join(BASE_DIR, "business_rules.csv")
    return pd.read_csv(path).to_dict(orient="records")
