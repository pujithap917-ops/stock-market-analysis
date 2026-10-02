
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Stock Market Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Market Analysis Dashboard")
st.write(
    "Analyze historical stock prices, compare companies, "
    "and explore market trends."
)

DATA_FOLDER = Path("data")

# ---------------- LOAD DATA ----------------
def load_stock_data():
    frames = []

    if not DATA_FOLDER.exists():
        return pd.DataFrame()

    files = list(DATA_FOLDER.glob("*.csv"))
    files += list(DATA_FOLDER.glob("*.xlsx"))
    files += list(DATA_FOLDER.glob("*.xls"))

    for file in files:
        try:
            if file.suffix.lower() == ".csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            if df.empty:
                continue

            # Standardize column names
            df.columns = [
                str(col).strip().lower().replace(" ", "_")
                for col in df.columns
            ]

            # Find date column
            date_options = [
                "date", "datetime", "timestamp", "trade_date"
            ]
            date_col = next(
                (c for c in date_options if c in df.columns), None
            )

            # Find closing price column
            close_options = [
                "close", "closing_price", "close_price",
                "adj_close", "adjusted_close", "price",
                "last_price"
            ]
            close_col = next(
                (c for c in close_options if c in df.columns), None
            )

            if date_col is None or close_col is None:
                st.warning(
                    f"Skipped {file.name}: date or closing-price "
                    "column was not recognized."
                )
                continue

            df["Date"] = pd.to_datetime(
                df[date_col], errors="coerce", dayfirst=True
            )
            df["Close"] = pd.to_numeric(
                df[close_col].astype(str).str.replace(",", ""),
                errors="coerce"
            )

            # Company name from filename
            company = file.stem.replace("_", " ").title()
            df["Company"] = company

            # Find optional volume column
            volume_col = next(
                (c for c in ["volume", "traded_volume"]
                 if c in df.columns), None
            )

            if volume_col:
                df["Volume"] = pd.to_numeric(
                    df[volume_col].astype(str).str.replace(",", ""),
                    errors="coerce"
                )

            df = df.dropna(subset=["Date", "Close"])
            frames.append(df)

        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True).sort_values("Date")


stock_df = load_stock_data()

# ---------------- CHECK DATA ----------------
if stock_df.empty:
    st.error("No usable stock data found.")
    st.info(
        "Place your CSV or Excel files inside the 'data' folder. "
        "Each file must contain a date column and a closing-price "
        "column, such as Date and Close."
    )
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Dashboard Filters")

companies = sorted(stock_df["Company"].unique())

selected_companies = st.sidebar.multiselect(
    "Select companies",
    companies,
    default=companies
)

min_date = stock_df["Date"].min().date()
max_date = stock_df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = stock_df[
    stock_df["Company"].isin(selected_companies)
].copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        & (filtered_df["Date"].dt.date <= end_date)
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------- KPI CARDS ----------------
latest = (
    filtered_df.sort_values("Date")
    .groupby("Company", as_index=False)
    .tail(1)
)

first_prices = (
    filtered_df.sort_values("Date")
    .groupby("Company", as_index=False)
    .head(1)
)

total_companies = filtered_df["Company"].nunique()
total_records = len(filtered_df)
average_close = filtered_df["Close"].mean()

if total_companies == 1:
    company_first = first_prices.iloc[0]["Close"]
    company_last = latest.iloc[0]["Close"]

    if company_first != 0:
        price_change = (
            (company_last - company_first) / company_first
        ) * 100
    else:
        price_change = 0
else:
    price_change = None

c1, c2, c3, c4 = st.columns(4)

c1.metric("Companies", f"{total_companies}")
c2.metric("Total Records", f"{total_records:,}")
c3.metric("Average Closing Price", f"{average_close:,.2f}")

if price_change is not None:
    c4.metric("Price Change", f"{price_change:+.2f}%")
else:
    c4.metric("Price Change", "Select one company")

st.divider()

# ---------------- PRICE TREND ----------------
st.subheader("📉 Historical Stock Price Trends")

fig = px.line(
    filtered_df.sort_values("Date"),
    x="Date",
    y="Close",
    color="Company",
    title="Closing Price Over Time",
    labels={
        "Date": "Date",
        "Close": "Closing Price",
        "Company": "Company"
    }
)

fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ---------------- LATEST PRICES ----------------
st.subheader("💰 Latest Available Closing Prices")

latest_prices = (
    filtered_df.sort_values("Date")
    .groupby("Company", as_index=False)
    .tail(1)[["Company", "Date", "Close"]]
    .sort_values("Close", ascending=False)
)

st.dataframe(
    latest_prices,
    use_container_width=True,
    hide_index=True
)

# ---------------- COMPANY COMPARISON ----------------
st.subheader("📊 Closing Price Comparison")

comparison = px.bar(
    latest_prices,
    x="Company",
    y="Close",
    color="Company",
    title="Latest Closing Price by Company",
    labels={"Close": "Closing Price"}
)

st.plotly_chart(comparison, use_container_width=True)

# ---------------- SUMMARY TABLE ----------------
st.subheader("📋 Stock Data Summary")

summary = filtered_df.groupby("Company").agg(
    First_Date=("Date", "min"),
    Latest_Date=("Date", "max"),
    Lowest_Close=("Close", "min"),
    Highest_Close=("Close", "max"),
    Average_Close=("Close", "mean"),
    Records=("Close", "count")
).reset_index()

summary["Average_Close"] = summary["Average_Close"].round(2)
summary["Lowest_Close"] = summary["Lowest_Close"].round(2)
summary["Highest_Close"] = summary["Highest_Close"].round(2)

st.dataframe(summary, use_container_width=True, hide_index=True)

# ---------------- DOWNLOAD ----------------
st.subheader("⬇️ Download Results")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Stock Data (CSV)",
    data=csv_data,
    file_name="stock_market_analysis.csv",
    mime="text/csv"
)

st.success("Stock Market Analysis Dashboard loaded successfully.")