# backend/utils.py

import platform
import psutil
import uuid
import socket
import hashlib
import pandas as pd
import os

def get_machine_info():
    try:
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
            "ram": f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB"
        }
    except Exception as e:
        return {"error": str(e)}

def generate_hash_for_machine():
    info = get_machine_info()
    raw = ''.join([str(v) for v in info.values() if v])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def load_dataset(csv_path):
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
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
