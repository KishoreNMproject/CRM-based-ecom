
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.title("Customer Analytics Dashboard")

rfm_data = requests.get("http://localhost:8000/rfm").json()
rfm = pd.DataFrame(rfm_data)

st.subheader("RFM Data")
st.dataframe(rfm.head())

st.subheader("RFM Scatter Plot")
plt.scatter(rfm['Recency'], rfm['Monetary'], c=rfm['Frequency'], cmap='viridis')
plt.xlabel("Recency")
plt.ylabel("Monetary")
st.pyplot(plt)
