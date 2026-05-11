# 💰 Personal Finance Dashboard

An end-to-end personal finance analytics dashboard built with Python, SQL, and data science libraries. This project demonstrates a full data pipeline — from database design and synthetic data generation to machine learning models and an interactive web dashboard.

---

## 🚀 Features

- **SQL Database** — Normalized SQLite schema with transactions, merchants, and categories
- **Data Pipeline** — Automated data generation and loading with pandas
- **Exploratory Analysis** — Spending breakdowns, budget variance, and monthly trends
- **Anomaly Detection** — Flags unusual transactions using Isolation Forest
- **Spending Forecast** — Predicts next month's spending with linear regression
- **Interactive Dashboard** — Fully interactive Streamlit app with filters and charts

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| SQLite + sqlite3 | Database design and querying |
| pandas | Data loading, cleaning, and analysis |
| NumPy | Statistical calculations |
| scikit-learn | K-Means clustering, Isolation Forest, Linear Regression |
| Matplotlib / Seaborn | Exploratory visualizations |
| Plotly | Interactive dashboard charts |
| Streamlit | Web dashboard framework |
| Faker | Synthetic transaction data generation |

---

## 📁 Project Structure
finance_dashboard/
├── data/
│   ├── setup_db.py              # Creates the SQLite schema
│   ├── generate_data.py         # Generates synthetic transaction data
│   ├── load_data.py             # Loads and previews data with pandas
│   ├── finance.db               # SQLite database
│   ├── transactions_analyzed.csv
│   └── anomalies.csv
├── notebooks/
│   ├── analysis.py              # Exploratory data analysis
│   └── ml_models.py             # Machine learning models
├── main.py                      # Streamlit dashboard
└── README.md

---

## ⚙️ Setup & Installation

1. **Clone the repository**
```bash
git clone https://github.com/bonillaj4atwit/finance_dashboard.git
cd finance_dashboard
```

2. **Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install pandas numpy scikit-learn matplotlib seaborn streamlit plotly faker
```

4. **Set up the database and generate data**
```bash
python3 data/setup_db.py
python3 data/generate_data.py
```

5. **Run the dashboard**
```bash
streamlit run main.py
```

---

## 🤖 Machine Learning Models

**K-Means Clustering** groups transactions into 7 clusters based on amount, merchant, and time features — mapping spending behavior to categories automatically.

**Isolation Forest** learns the pattern of normal transactions and flags outliers as potential anomalies, achieving a silhouette score of 0.217 on synthetic data.

**Linear Regression** forecasts next month's total spending based on the 12-month trend.

---

## 📊 Dashboard Preview

The interactive dashboard includes:
- Summary metric cards (total spend, transaction count, averages)
- Spending by category bar and pie charts
- Monthly spending trend line chart
- Budget variance chart with over/under indicators
- Flagged anomalous transactions table
- Next month spending forecast
- Filterable raw transactions table

---

## 📝 Notes

Transaction data is synthetically generated using the Faker library to simulate realistic spending patterns while preserving data privacy. 

---

## 👩‍💻 Author

**Jasmine Bonilla**  
[GitHub](https://github.com/bonillaj4atwit) · [LinkedIn](https://linkedin.com/in/jasminebonilla06)