# 📈 Stock Market Analysis

## Project Overview

This project analyzes historical stock market data for six Indian companies: Bajaj Auto, Eicher Motors, Hero MotoCorp, Infosys, TCS, and TVS Motors.

The project uses Python, SQL, Pandas, and Streamlit to explore historical stock prices, compare company performance, and visualize trends.

## Objectives

* Analyze historical stock prices.
* Calculate percentage changes in closing prices.
* Compare price trends across six companies.
* Perform SQL-based data analysis.
* Build an interactive Streamlit dashboard.

## Companies Analyzed

1. Bajaj Auto
2. Eicher Motors
3. Hero MotoCorp
4. Infosys
5. Tata Consultancy Services (TCS)
6. TVS Motors

## Tools and Technologies

* Python
* SQL and MySQL Workbench
* Pandas
* Streamlit
* Plotly
* Excel and CSV

## Dashboard Features

* Company selection and date filters
* Stock price trend charts
* Latest available closing prices
* Average, highest, and lowest closing prices
* Company comparison charts
* Filtered data export to CSV

## Project Structure

```text
stock-market-analysis/
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── bajaj_auto.csv
    ├── eicher_motors.csv
    ├── hero_motocorp.csv
    ├── infosys.csv
    ├── tcs.csv
    └── tvs_motors.csv
```

*The filenames shown above are examples. Use your actual dataset filenames.*

## How to Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add the datasets

Place your stock data files inside the `data` folder.

### 3. Run the dashboard

```bash
streamlit run app.py
```

### 4. Explore the dashboard

Open the local URL displayed in the terminal and select companies and date ranges to analyze their historical data.

## Historical Data

The supplied datasets cover the period from January 2015 to July 2018. The analysis is based on the provided historical records and does not represent live market prices.

## Project Deliverables

* SQL analysis queries
* Interactive Streamlit dashboard
* Project report in PDF format
* Project presentation and walkthrough video

## Conclusion

This project demonstrates how historical stock data can be analyzed using SQL and Python, summarized through data analysis, and presented using interactive visualizations.

**Note:** Historical price movements do not guarantee future performance and should not be treated as investment advice.
