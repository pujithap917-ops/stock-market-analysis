import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Stock Market Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Market Analysis Dashboard")
st.write(
    "Analyze historical stock prices, compare companies, "
    "identify market trends, and generate business insights."
)

# ============================================================
# FOLDER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

st.write(f"📂 **Dashboard folder:** `{BASE_DIR}`")


# ============================================================
# FILES
# ============================================================

FILES = {
    "Bajaj Auto": "Bajaj Auto.csv",
    "Eicher Motors": "Eicher Motors.csv",
    "Hero Motocorp": "Hero Motocorp.csv",
    "Infosys": "Infosys.csv",
    "TCS": "TCS.csv",
    "TVS Motors": "TVS Motors.csv"
}


# ============================================================
# READ CSV
# ============================================================

def read_csv_file(path):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
        "utf-16"
    ]

    for encoding in encodings:

        try:

            df = pd.read_csv(
                path,
                encoding=encoding
            )

            return df, encoding

        except UnicodeDecodeError:
            continue

    return None, None


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(df, names):

    # Exact match
    for name in names:

        if name in df.columns:
            return name

    # Flexible match
    for column in df.columns:

        clean = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if clean in names:
            return column

    return None


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = []
    messages = []

    for company, filename in FILES.items():

        path = BASE_DIR / filename

        # Check file
        if not path.exists():

            messages.append(
                f"❌ {company}: File not found"
            )

            continue

        # Read file
        df, encoding = read_csv_file(path)

        if df is None:

            messages.append(
                f"❌ {company}: Could not read CSV"
            )

            continue

        # Clean column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace("\ufeff", "", regex=False)
        )

        # Find Date
        date_col = find_column(
            df,
            [
                "date",
                "datetime",
                "timestamp",
                "date_time"
            ]
        )

        # Find Close
        close_col = find_column(
            df,
            [
                "close",
                "close_price",
                "closing_price",
                "adj_close",
                "adjusted_close"
            ]
        )

        # Check Date
        if date_col is None:

            messages.append(
                f"❌ {company}: Date column not found. "
                f"Columns = {list(df.columns)}"
            )

            continue

        # Check Close
        if close_col is None:

            messages.append(
                f"❌ {company}: Close column not found. "
                f"Columns = {list(df.columns)}"
            )

            continue

        # Convert Date
        df["Date"] = pd.to_datetime(
            df[date_col],
            errors="coerce"
        )

        # Convert Close
        df["Close"] = pd.to_numeric(
            df[close_col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip(),
            errors="coerce"
        )

        # Company
        df["Company"] = company

        # Remove invalid rows
        df = df.dropna(
            subset=["Date", "Close"]
        )

        if df.empty:

            messages.append(
                f"❌ {company}: No valid Date/Close data"
            )

            continue

        # Keep columns
        df = df[
            [
                "Date",
                "Close",
                "Company"
            ]
        ]

        data.append(df)

        messages.append(
            f"✅ {company}: Loaded successfully "
            f"using {encoding}"
        )

    if not data:

        return pd.DataFrame(), messages

    final = pd.concat(
        data,
        ignore_index=True
    )

    final = final.sort_values(
        ["Company", "Date"]
    )

    # Daily return
    final["Daily_Return"] = (
        final
        .groupby("Company")["Close"]
        .pct_change()
        * 100
    )

    return final, messages


# ============================================================
# LOAD
# ============================================================

df, messages = load_data()


# ============================================================
# DEBUG INFORMATION
# ============================================================

with st.expander(
    "📂 Data Loading Details",
    expanded=True
):

    for message in messages:

        if message.startswith("✅"):
            st.success(message)
        else:
            st.error(message)


# ============================================================
# STOP IF NO DATA
# ============================================================

if df.empty:

    st.error("❌ No stock data could be loaded.")

    st.info(
        "The CSV files were found, but their Date/Close "
        "columns could not be read."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Filters")

companies = sorted(
    df["Company"].unique()
)

selected_companies = st.sidebar.multiselect(
    "Select Companies",
    companies,
    default=companies
)


# ============================================================
# DATE FILTER
# ============================================================

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# FILTER
# ============================================================

filtered = df[
    df["Company"].isin(selected_companies)
].copy()

if len(date_range) == 2:

    filtered = filtered[
        (filtered["Date"].dt.date >= date_range[0]) &
        (filtered["Date"].dt.date <= date_range[1])
    ]


if filtered.empty:

    st.warning(
        "No data available for selected filters."
    )

    st.stop()


# ============================================================
# KPIs
# ============================================================

st.subheader("📊 Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "🏢 Companies",
    filtered["Company"].nunique()
)

c2.metric(
    "📋 Records",
    f"{len(filtered):,}"
)

c3.metric(
    "💰 Average Price",
    f"₹{filtered['Close'].mean():,.2f}"
)

c4.metric(
    "⬆️ Highest Price",
    f"₹{filtered['Close'].max():,.2f}"
)

c5.metric(
    "📈 Avg Daily Return",
    f"{filtered['Daily_Return'].mean():.2f}%"
)


st.divider()


# ============================================================
# CHART 1
# ============================================================

st.subheader("📈 Historical Stock Price Trend")

fig1 = px.line(
    filtered.sort_values("Date"),
    x="Date",
    y="Close",
    color="Company",
    title="Historical Closing Price"
)

fig1.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ============================================================
# PERFORMANCE
# ============================================================

performance = []

for company in filtered["Company"].unique():

    temp = (
        filtered[
            filtered["Company"] == company
        ]
        .sort_values("Date")
    )

    if len(temp) < 2:
        continue

    first = temp["Close"].iloc[0]
    last = temp["Close"].iloc[-1]

    if first == 0:
        continue

    return_pct = (
        (last - first) / first
    ) * 100

    performance.append({
        "Company": company,
        "Starting Price": first,
        "Latest Price": last,
        "Return (%)": return_pct
    })


performance_df = pd.DataFrame(performance)


# ============================================================
# CHART 2
# ============================================================

st.subheader("🏆 Company Performance Comparison")

if not performance_df.empty:

    performance_df = performance_df.sort_values(
        "Return (%)",
        ascending=False
    )

    fig2 = px.bar(
        performance_df,
        x="Company",
        y="Return (%)",
        color="Company",
        text_auto=".2f",
        title="Stock Return by Company"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# CHART 3
# ============================================================

st.subheader("📉 Daily Return Analysis")

fig3 = px.line(
    filtered.sort_values("Date"),
    x="Date",
    y="Daily_Return",
    color="Company",
    title="Daily Stock Returns (%)"
)

fig3.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ============================================================
# LATEST PRICES
# ============================================================

st.subheader("💰 Latest Stock Prices")

latest = (
    filtered
    .sort_values("Date")
    .groupby("Company")
    .tail(1)
    [["Company", "Date", "Close"]]
    .sort_values(
        "Close",
        ascending=False
    )
)

st.dataframe(
    latest,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CHART 4
# ============================================================

st.subheader("📊 Latest Price Comparison")

fig4 = px.bar(
    latest,
    x="Company",
    y="Close",
    color="Company",
    text_auto=".2f",
    title="Latest Closing Price"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ============================================================
# COMPANY SUMMARY
# ============================================================

st.subheader("📋 Company Summary")

summary = (
    filtered
    .groupby("Company")
    .agg(
        First_Date=("Date", "min"),
        Last_Date=("Date", "max"),
        Lowest_Price=("Close", "min"),
        Highest_Price=("Close", "max"),
        Average_Price=("Close", "mean"),
        Average_Daily_Return=("Daily_Return", "mean"),
        Records=("Close", "count")
    )
    .reset_index()
)

st.dataframe(
    summary.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# HIGHLIGHTS
# ============================================================

if not performance_df.empty:

    st.subheader("🏆 Performance Highlights")

    best = performance_df.iloc[0]
    worst = performance_df.iloc[-1]

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"""
            🥇 **Best Performing Company**

            **{best['Company']}**

            Return: **{best['Return (%)']:.2f}%**
            """
        )

    with col2:

        st.error(
            f"""
            📉 **Lowest Performing Company**

            **{worst['Company']}**

            Return: **{worst['Return (%)']:.2f}%**
            """
        )


# ============================================================
# KEY INSIGHTS
# ============================================================

st.subheader("🔍 Key Insights")

if not performance_df.empty:

    positive = (
        performance_df["Return (%)"] > 0
    ).sum()

    negative = (
        performance_df["Return (%)"] < 0
    ).sum()

    average_return = (
        performance_df["Return (%)"].mean()
    )

    st.write(
        f"• **{positive}** companies show positive returns."
    )

    st.write(
        f"• **{negative}** companies show negative returns."
    )

    st.write(
        f"• Average company return: "
        f"**{average_return:.2f}%**."
    )

    st.write(
        f"• Best performer: **{best['Company']}** "
        f"with **{best['Return (%)']:.2f}%**."
    )

    st.write(
        f"• Lowest performer: **{worst['Company']}** "
        f"with **{worst['Return (%)']:.2f}%**."
    )


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("💡 Business Recommendations")

st.markdown("""
### 1. Monitor high-performing companies
Track companies showing strong positive returns.

### 2. Investigate underperforming companies
Analyze companies showing negative returns and identify
possible market or company-specific reasons.

### 3. Monitor volatility
Daily returns can help identify price fluctuations and risk.

### 4. Diversify
Comparing multiple companies can reduce dependence on one stock.

### 5. Focus on long-term trends
Long-term price movements are more useful than individual
daily fluctuations.

### 6. Combine stock and financial data
Combine stock prices with revenue, profit, EPS and P/E ratio
for deeper analysis.

### 7. Regular monitoring
Use the dashboard to monitor changes in stock performance.
""")


# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("⬇️ Download Filtered Data")

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📥 Download CSV",
    data=csv,
    file_name="stock_market_analysis_filtered.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Stock Market Analysis Dashboard | "
    "Python | Pandas | Plotly | Streamlit"
)

st.caption(
    "For educational purposes only. "
    "This dashboard is not investment advice."
)
