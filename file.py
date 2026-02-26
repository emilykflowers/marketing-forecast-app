import streamlit as st
import pandas as pd
import sqlite3
from engine import run_forecast
import os

# Create DB folder if missing
os.makedirs("data", exist_ok=True)

DB_PATH = "data/marketing.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_data (
            date TEXT,
            channel TEXT,
            spend REAL,
            impressions REAL,
            clicks REAL,
            conversions REAL,
            revenue REAL
        )
    """)
    conn.commit()
    return conn

def insert_data(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("marketing_data", conn, if_exists="append", index=False)
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM marketing_data", conn)
    conn.close()
    return df

# Init DB
init_db()

st.title("Marketing Channel Forecast App (Cloud Version)")

st.header("Upload Daily Performance")

uploaded = st.file_uploader("Upload CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    st.write(df.head())

    if st.button("Upload to Database"):
        insert_data(df)
        st.success(f"Uploaded {len(df)} rows!")

st.header("Run Forecast")

days = st.number_input("Days to forecast", value=30)
budget_adj = st.number_input("Budget adjustment (%)", value=0.0)

if st.button("Generate Forecast"):
    df = load_data()

    if df.empty:
        st.error("No data found. Upload data first.")
    else:
        output = run_forecast(df, days, budget_adj / 100)
        out_df = pd.DataFrame(output)
        st.write(out_df)
        st.line_chart(out_df.set_index("date"))
