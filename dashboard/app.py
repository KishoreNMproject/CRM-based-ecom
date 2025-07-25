
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

def load_data():
    try:
        df = pd.read_csv("../backend/data/online_retail.csv")
        return df
    except:
        messagebox.showerror("Error", "Failed to load data.")
        return pd.DataFrame()

def plot_data():
    df = load_data()
    if df.empty:
        return
    df['Description'].value_counts().plot(kind='bar')
    plt.title("Top Products")
    plt.xlabel("Product")
    plt.ylabel("Views")
    plt.tight_layout()
    plt.show()

app = tk.Tk()
app.title("Analyst Dashboard")
app.geometry("800x600")

btn = ttk.Button(app, text="Show Analytics", command=plot_data)
btn.pack(pady=20)

app.mainloop()
