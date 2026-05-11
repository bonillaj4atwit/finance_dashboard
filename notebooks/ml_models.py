import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score

# ── Load ──────────────────────────────────────────────────────────────────────
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
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.dayofweek
df['week'] = df['date'].dt.isocalendar().week.astype(int)

print("Data loaded!")
print(f"Shape: {df.shape}")

# ── Encode ────────────────────────────────────────────────────────────────────
le_merchant = LabelEncoder()
le_category = LabelEncoder()

df['merchant_encoded'] = le_merchant.fit_transform(df['merchant'])
df['category_encoded'] = le_category.fit_transform(df['category'])

# Features for clustering
features = ['amount', 'merchant_encoded', 'month', 'day_of_week']
X = df[features]

print("\nFeature matrix shape:", X.shape)
print(X.head())

# ── K-Means clustering ────────────────────────────────────────────────────────
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=7, random_state=42, n_init=10))
])

pipeline.fit(X)
df['cluster'] = pipeline.named_steps['kmeans'].labels_

# Score the clustering quality (closer to 1.0 = better)
X_scaled = pipeline.named_steps['scaler'].transform(X)
score = silhouette_score(X_scaled, df['cluster'])
print(f"\nSilhouette score: {score:.3f}")

# See how clusters map to real categories
print("\n── Cluster vs Category breakdown ──")
print(pd.crosstab(df['cluster'], df['category']))

# ── Anomaly detection ─────────────────────────────────────────────────────────
anomaly_features = ['amount', 'merchant_encoded', 'month', 'day_of_week']

iso_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('isolation_forest', IsolationForest(
        contamination=0.05,  # expects ~5% of transactions to be anomalies
        random_state=42
    ))
])

df['anomaly'] = iso_pipeline.fit_predict(df[anomaly_features])
# IsolationForest returns -1 for anomalies, 1 for normal
df['is_anomaly'] = df['anomaly'] == -1

anomalies = df[df['is_anomaly']].sort_values('amount', ascending=False)

print(f"\n── Anomaly Detection Results ──")
print(f"Total transactions: {len(df)}")
print(f"Flagged as anomalies: {len(anomalies)} ({len(anomalies)/len(df)*100:.1f}%)")
print("\nTop 10 flagged transactions:")
print(anomalies[['date', 'amount', 'merchant', 'category']].head(10).to_string(index=False))

# ── Spending forecast ─────────────────────────────────────────────────────────
from sklearn.linear_model import LinearRegression

monthly_spend = df.groupby(df['date'].dt.to_period('M'))['amount'] \
                  .sum().reset_index()
monthly_spend.columns = ['month', 'total_spend']
monthly_spend['month_index'] = range(len(monthly_spend))

X_time = monthly_spend[['month_index']]
y_time = monthly_spend['total_spend']

model = LinearRegression()
model.fit(X_time, y_time)

next_index = [[len(monthly_spend)]]
predicted = model.predict(next_index)[0]

print(f"\n── Spending Forecast ──")
print(f"Predicted spend next month: ${predicted:,.2f}")
print(f"Model R² score: {model.score(X_time, y_time):.3f}")

# ── Save results ──────────────────────────────────────────────────────────────
df.to_csv('data/transactions_analyzed.csv', index=False)
anomalies[['date', 'amount', 'merchant', 'category']].to_csv(
    'data/anomalies.csv', index=False
)
print("\nResults saved to data/")
print("Phase 4 complete!")