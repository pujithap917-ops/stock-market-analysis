import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Stock Market Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📈 Stock Market Analysis Dashboard")

st.write(
    "Analyze historical stock prices, compare companies, "
    "identify market trends, and generate business insights."
)


# ============================================================
# PROJECT OVERVIEW
# ============================================================

with st.expander("📋 Project Overview", expanded=True):

    st.markdown("""
    ### Stock Market Analysis

    This project analyzes historical stock market data for
    six companies using Python, Pandas, Plotly and Streamlit.

    **Companies:**

    - Bajaj Auto
    - Eicher Motors
    - Hero Motocorp
    - Infosys
    - TCS
    - TVS Motors

    **Objectives:**

    - Analyze historical stock prices
    - Compare company performance
    - Analyze daily returns
    - Identify highest and lowest prices
    - Identify best-performing companies
    - Generate business recommendations
    """)


# ============================================================
# PROJECT FOLDER
# ============================================================

# IMPORTANT:
# This gets the folder where stock.py is located.
# Do NOT use .parent here.

PROJECT_FOLDER = Path(__file__).resolve().parent


# ============================================================
# STOCK FILES
# ============================================================

STOCK_FILES = {
    "Bajaj Auto": "Bajaj Auto.csv",
    "Eicher Motors": "Eicher Motors.csv",
    "Hero Motocorp": "Hero Motocorp.csv",
    "Infosys": "Infosys.csv",
    "TCS": "TCS.csv",
    "TVS Motors": "TVS Motors.csv"
}


# ============================================================
# FIND DATE COLUMN
# ============================================================

def find_date_column(df):

    possible_columns = [
        "Date",
        "date",
        "DATE",
        "Datetime",
        "datetime",
        "Timestamp",
        "timestamp"
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    # Flexible search
    for column in df.columns:

        clean_column = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if clean_column in [
            "date",
            "datetime",
            "timestamp"
        ]:
            return column

    return None


# ============================================================
# FIND CLOSE COLUMN
# ============================================================

def find_close_column(df):

    possible_columns = [
        "Close",
        "close",
        "CLOSE",
        "Close Price",
        "close_price",
        "Closing Price",
        "closing_price",
        "Adj Close",
        "adj_close",
        "adjusted_close"
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    # Flexible search
    for column in df.columns:

        clean_column = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if clean_column in [
            "close",
            "close_price",
            "closing_price",
            "adj_close",
            "adjusted_close"
        ]:
            return column

    return None


# ============================================================
# LOAD STOCK DATA
# ============================================================

@st.cache_data
def load_stock_data():

    all_data = []
    problems = []

    for company, filename in STOCK_FILES.items():

        file_path = PROJECT_FOLDER / filename

        # Check file
        if not file_path.exists():

            problems.append(
                f"{company}: File not found - {filename}"
            )

            continue

        try:

            # Read CSV
            df = pd.read_csv(
                file_path,
                encoding="utf-8-sig"
            )

            # Check empty
            if df.empty:

                problems.append(
                    f"{company}: CSV file is empty"
                )

                continue

            # Clean column names
            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            # Find columns
            date_column = find_date_column(df)
            close_column = find_close_column(df)

            # Check Date
            if date_column is None:

                problems.append(
                    f"{company}: Date column not found. "
                    f"Columns found: {list(df.columns)}"
                )

                continue

            # Check Close
            if close_column is None:

                problems.append(
                    f"{company}: Close column not found. "
                    f"Columns found: {list(df.columns)}"
                )

                continue

            # Convert Date
            df["Date"] = pd.to_datetime(
                df[date_column],
                errors="coerce"
            )

            # Convert Close
            df["Close"] = pd.to_numeric(
                df[close_column]
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

            # Check again
            if df.empty:

                problems.append(
                    f"{company}: No valid Date/Close rows"
                )

                continue

            # Keep required columns
            df = df[
                [
                    "Date",
                    "Close",
                    "Company"
                ]
            ]

            all_data.append(df)

        except Exception as e:

            problems.append(
                f"{company}: {str(e)}"
            )

    # No data
    if not all_data:

        return pd.DataFrame(), problems

    # Combine
    final_df = pd.concat(
        all_data,
        ignore_index=True
    )

    # Sort
    final_df = final_df.sort_values(
        ["Company", "Date"]
    )

    # Daily return
    final_df["Daily_Return"] = (
        final_df
        .groupby("Company")["Close"]
        .pct_change()
        * 100
    )

    return final_df, problems


# ============================================================
# LOAD DATA
# ============================================================

df, problems = load_stock_data()


# ============================================================
# DATA ERROR MESSAGE
# ============================================================

if problems:

    with st.expander(
        "⚠️ Data Loading Details",
        expanded=True
    ):

        st.write(
            f"Dashboard folder: `{PROJECT_FOLDER}`"
        )

        for problem in problems:
            st.warning(problem)


# ============================================================
# NO DATA
# ============================================================

if df.empty:

    st.error("❌ No stock data could be loaded.")

    st.info("""
    Make sure your files are placed in the SAME folder as
    `stock.py`:

    • Bajaj Auto.csv
    • Eicher Motors.csv
    • Hero Motocorp.csv
    • Infosys.csv
    • TCS.csv
    • TVS Motors.csv

    Each CSV should contain a Date column and a Close column.
    """)

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Filters")


# ============================================================
# COMPANY FILTER
# ============================================================

company_list = sorted(
    df["Company"].unique()
)

selected_companies = st.sidebar.multiselect(
    "Select Companies",
    company_list,
    default=company_list
)


# ============================================================
# DATE FILTER
# ============================================================

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["Company"].isin(selected_companies)
].copy()


if len(selected_dates) == 2:

    start_date = selected_dates[0]
    end_date = selected_dates[1]

    filtered_df = filtered_df[
        (
            filtered_df["Date"].dt.date >= start_date
        )
        &
        (
            filtered_df["Date"].dt.date <= end_date
        )
    ]


# ============================================================
# CHECK FILTERED DATA
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_companies = filtered_df[
    "Company"
].nunique()

total_records = len(filtered_df)

average_price = filtered_df[
    "Close"
].mean()

highest_price = filtered_df[
    "Close"
].max()

lowest_price = filtered_df[
    "Close"
].min()

average_return = filtered_df[
    "Daily_Return"
].mean()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        "🏢 Companies",
        total_companies
    )

with kpi2:
    st.metric(
        "📋 Records",
        f"{total_records:,}"
    )

with kpi3:
    st.metric(
        "💰 Average Price",
        f"₹{average_price:,.2f}"
    )

with kpi4:
    st.metric(
        "⬆️ Highest Price",
        f"₹{highest_price:,.2f}"
    )

with kpi5:
    st.metric(
        "📈 Avg Daily Return",
        f"{average_return:.2f}%"
    )


st.divider()


# ============================================================
# CHART 1
# HISTORICAL STOCK PRICE
# ============================================================

st.subheader("📈 Historical Stock Price Trend")

price_chart = px.line(
    filtered_df.sort_values("Date"),
    x="Date",
    y="Close",
    color="Company",
    title="Historical Closing Price"
)

price_chart.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    price_chart,
    use_container_width=True
)


# ============================================================
# COMPANY PERFORMANCE
# ============================================================

performance_list = []

for company in filtered_df["Company"].unique():

    company_df = (
        filtered_df[
            filtered_df["Company"] == company
        ]
        .sort_values("Date")
    )

    if len(company_df) < 2:
        continue

    starting_price = company_df[
        "Close"
    ].iloc[0]

    ending_price = company_df[
        "Close"
    ].iloc[-1]

    if starting_price == 0:
        continue

    return_percentage = (
        (
            ending_price - starting_price
        )
        / starting_price
        * 100
    )

    performance_list.append({
        "Company": company,
        "Starting Price": starting_price,
        "Latest Price": ending_price,
        "Return (%)": return_percentage
    })


performance_df = pd.DataFrame(
    performance_list
)


# ============================================================
# CHART 2
# COMPANY PERFORMANCE
# ============================================================

st.subheader("🏆 Company Performance Comparison")

if not performance_df.empty:

    performance_df = performance_df.sort_values(
        "Return (%)",
        ascending=False
    )

    performance_chart = px.bar(
        performance_df,
        x="Company",
        y="Return (%)",
        color="Company",
        title="Stock Return by Company",
        text_auto=".2f"
    )

    st.plotly_chart(
        performance_chart,
        use_container_width=True
    )


# ============================================================
# CHART 3
# DAILY RETURNS
# ============================================================

st.subheader("📉 Daily Return Analysis")

return_chart = px.line(
    filtered_df.sort_values("Date"),
    x="Date",
    y="Daily_Return",
    color="Company",
    title="Daily Stock Returns (%)"
)

return_chart.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    return_chart,
    use_container_width=True
)


# ============================================================
# LATEST PRICE TABLE
# ============================================================

st.subheader("💰 Latest Stock Prices")

latest_prices = (
    filtered_df
    .sort_values("Date")
    .groupby("Company")
    .tail(1)
)

latest_prices = latest_prices[
    [
        "Company",
        "Date",
        "Close"
    ]
].sort_values(
    "Close",
    ascending=False
)

st.dataframe(
    latest_prices,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CHART 4
# LATEST PRICE COMPARISON
# ============================================================

st.subheader("📊 Latest Price Comparison")

latest_chart = px.bar(
    latest_prices,
    x="Company",
    y="Close",
    color="Company",
    title="Latest Closing Price",
    text_auto=".2f"
)

st.plotly_chart(
    latest_chart,
    use_container_width=True
)


# ============================================================
# COMPANY SUMMARY
# ============================================================

st.subheader("📋 Company Summary")

summary_df = (
    filtered_df
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

summary_df = summary_df.round(2)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PERFORMANCE HIGHLIGHTS
# ============================================================

if not performance_df.empty:

    st.subheader("🏆 Performance Highlights")

    best_company = performance_df.iloc[0]
    worst_company = performance_df.iloc[-1]

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"""
            🥇 **Best Performing Company**

            **{best_company['Company']}**

            Return: **{best_company['Return (%)']:.2f}%**
            """
        )

    with col2:

        st.error(
            f"""
            📉 **Lowest Performing Company**

            **{worst_company['Company']}**

            Return: **{worst_company['Return (%)']:.2f}%**
            """
        )


# ============================================================
# KEY INSIGHTS
# ============================================================

st.subheader("🔍 Key Insights")

if not performance_df.empty:

    positive_companies = len(
        performance_df[
            performance_df["Return (%)"] > 0
        ]
    )

    negative_companies = len(
        performance_df[
            performance_df["Return (%)"] < 0
        ]
    )

    average_company_return = (
        performance_df["Return (%)"].mean()
    )

    st.write(
        f"• **{positive_companies}** selected companies "
        "show a positive return."
    )

    st.write(
        f"• **{negative_companies}** selected companies "
        "show a negative return."
    )

    st.write(
        f"• Average company return is "
        f"**{average_company_return:.2f}%**."
    )

    st.write(
        f"• Best performer is **{best_company['Company']}** "
        f"with **{best_company['Return (%)']:.2f}%** return."
    )

    st.write(
        f"• Lowest performer is **{worst_company['Company']}** "
        f"with **{worst_company['Return (%)']:.2f}%** return."
    )


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("💡 Business Recommendations")

st.markdown("""
### 1. Monitor high-performing companies
Companies with strong positive returns can be analyzed
further for investment and business performance factors.

### 2. Investigate underperforming companies
Companies with negative returns should be investigated for
possible market, industry and company-specific factors.

### 3. Monitor stock volatility
Daily returns should be monitored to understand price
fluctuations and potential risk.

### 4. Diversify
Comparing multiple companies can help reduce dependence
on a single stock.

### 5. Focus on long-term trends
Long-term price movements provide more meaningful insights
than individual daily fluctuations.

### 6. Combine stock and financial data
Stock prices should be analyzed together with revenue,
profit, EPS, P/E ratio and other financial indicators.

### 7. Regular monitoring
The dashboard can be used to monitor changes in stock
prices and company performance over time.
""")


# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("⬇️ Download Filtered Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📥 Download CSV",
    data=csv_data,
    file_name="stock_market_analysis_filtered.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Stock Market Analysis Dashboard | "
    "Python | Pandas | Streamlit | Plotly"
)

st.caption(
    "For educational and analytical purposes only. "
    "This dashboard is not investment advice."
)