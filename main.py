import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Dashboard")
st.markdown("A data science project analyzing personal spending patterns.")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect('data/finance.db')
    df = pd.read_sql_query('''
        SELECT 
            t.date,
            t.amount,
            m.name AS merchant,
            c.name AS category,
            c.budget
        FROM transactions t
        JOIN merchants m ON t.merchant_id = m.id
        JOIN categories c ON m.category_id = c.id
        ORDER BY t.date
    ''', conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    df['day_of_week'] = df['date'].dt.day_name()
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

categories = ['All'] + sorted(df['category'].unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

months = sorted(df['month'].astype(str).unique().tolist())
selected_month = st.sidebar.selectbox("Month", ['All'] + months)

if selected_category != 'All':
    df = df[df['category'] == selected_category]

if selected_month != 'All':
    df = df[df['month'].astype(str) == selected_month]

# ── Metric cards ──────────────────────────────────────────────────────────────
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Spend", f"${df['amount'].sum():,.2f}")
col2.metric("Transactions", f"{len(df):,}")
col3.metric("Avg Transaction", f"${df['amount'].mean():,.2f}")
col4.metric("Largest Purchase", f"${df['amount'].max():,.2f}")

st.divider()

# ── Charts row 1 ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spending by Category")
    category_spend = df.groupby('category')['amount'].sum().reset_index()
    fig = px.bar(
        category_spend,
        x='category',
        y='amount',
        color='category',
        labels={'amount': 'Total Spend ($)', 'category': 'Category'},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Spending Breakdown")
    fig = px.pie(
        category_spend,
        values='amount',
        names='category',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Monthly trend ─────────────────────────────────────────────────────────────
st.subheader("Monthly Spending Trend")
monthly_total = df.groupby(df['date'].dt.to_period('M'))['amount'] \
                  .sum().reset_index()
monthly_total.columns = ['month', 'total_spend']
monthly_total['month'] = monthly_total['month'].astype(str)

fig = px.line(
    monthly_total,
    x='month',
    y='total_spend',
    markers=True,
    labels={'total_spend': 'Total Spend ($)', 'month': 'Month'}
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Budget variance ───────────────────────────────────────────────────────────
st.subheader("Budget Variance")
monthly_spend = df.groupby(['category', 'budget'])['amount'].sum().reset_index()
monthly_spend.columns = ['category', 'budget', 'spent']
monthly_spend['variance'] = monthly_spend['budget'] - monthly_spend['spent']
monthly_spend['status'] = monthly_spend['variance'].apply(
    lambda x: '✅ Under budget' if x >= 0 else '🚨 Over budget'
)

fig = px.bar(
    monthly_spend,
    x='category',
    y='variance',
    color='status',
    color_discrete_map={
        '✅ Under budget': '#2ecc71',
        '🚨 Over budget': '#e74c3c'
    },
    labels={'variance': 'Variance ($)', 'category': 'Category'}
)
fig.add_hline(y=0, line_dash='dash', line_color='gray')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── ML section ────────────────────────────────────────────────────────────────
st.subheader("🤖 Machine Learning Insights")

@st.cache_data
def run_ml(dataframe):
    df_ml = load_data()  # always use full dataset for ML
    le_merchant = LabelEncoder()
    df_ml['merchant_encoded'] = le_merchant.fit_transform(df_ml['merchant'])
    df_ml['month_num'] = df_ml['date'].dt.month
    df_ml['day_of_week_num'] = df_ml['date'].dt.dayofweek

    features = ['amount', 'merchant_encoded', 'month_num', 'day_of_week_num']
    X = df_ml[features]

    # Anomaly detection
    iso_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('iso', IsolationForest(contamination=0.05, random_state=42))
    ])
    df_ml['anomaly'] = iso_pipeline.fit_predict(X)
    df_ml['is_anomaly'] = df_ml['anomaly'] == -1

    # Forecast
    monthly = df_ml.groupby(df_ml['date'].dt.to_period('M'))['amount'] \
                   .sum().reset_index()
    monthly.columns = ['month', 'total']
    monthly['month_index'] = range(len(monthly))
    reg = LinearRegression()
    reg.fit(monthly[['month_index']], monthly['total'])
    next_pred = reg.predict([[len(monthly)]])[0]

    return df_ml, next_pred

df_ml, next_pred = run_ml(df)
anomalies = df_ml[df_ml['is_anomaly']].sort_values('amount', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🚨 Flagged Transactions")
    st.markdown(f"**{len(anomalies)}** unusual transactions detected.")
    st.dataframe(
        anomalies[['date', 'amount', 'merchant', 'category']] \
                 .head(10) \
                 .reset_index(drop=True),
        use_container_width=True
    )

with col2:
    st.markdown("#### 📈 Next Month Forecast")
    st.metric("Predicted Spend", f"${next_pred:,.2f}")
    st.markdown("Based on your 12-month spending trend using linear regression.")

st.divider()

# ── Raw data ──────────────────────────────────────────────────────────────────
st.subheader("Raw Transactions")
st.dataframe(
    df[['date', 'amount', 'merchant', 'category']].reset_index(drop=True),
    use_container_width=True
)