
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

def load_data():
    try:
        df = pd.read_csv("../backend/data/analytics_data.csv")
        return df
    except:
        messagebox.showerror("Error", "Failed to load data.")
        return pd.DataFrame()

def plot_data():
    df = load_data()
    if df.empty:
        return
    df['product'].value_counts().plot(kind='bar')
    plt.title("Top Products")
    plt.xlabel("Product")
    plt.ylabel("Views")
    plt.tight_layout()
    plt.show()

app = tk.Tk()
app.title("Analyst Dashboard")
app.geometry("400x200")

btn = ttk.Button(app, text="Show Analytics", command=plot_data)
btn.pack(pady=20)

app.mainloop()
