
import os
import pandas as pd
import streamlit as st

st.title("Stock Market Analysis Dashboard")

stock_files = [
    "Bajaj Auto.csv",
    "Eicher Motors.csv",
    "Hero Motocorp.csv",
    "Infosys.csv",
    "TCS.csv",
    "TVS Motors.csv",
]

for file in stock_files:
    if not os.path.exists(file):
        st.error(f"Missing file: {file}")
        st.write("Current folder:", os.getcwd())
        st.stop()

    df = pd.read_csv(file)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    required_columns = ["Date", "Close"]
    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        st.error(
            f"{file} is missing columns: {missing}. "
            f"Available columns: {df.columns.tolist()}"
        )
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Date", "Close"])

    st.success(f"{file} loaded successfully")

st.success("All six stock CSV files are ready!")
