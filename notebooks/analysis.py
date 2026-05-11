import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

# ── Prepare ───────────────────────────────────────────────────────────────────
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M')
df['day_of_week'] = df['date'].dt.day_name()

print("Data loaded!")
print(df.info())

# ── Spending by category ───────────────────────────────────────────────────────
category_spend = df.groupby('category')['amount'].sum().sort_values(ascending=False)
print("\n── Total spend by category ──")
print(category_spend.round(2))

plt.figure(figsize=(10, 5))
sns.barplot(x=category_spend.index, y=category_spend.values, hue=category_spend.index, palette='Blues_d', legend=False)
plt.title('Total Spending by Category')
plt.ylabel('Amount ($)')
plt.xlabel('Category')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('data/spending_by_category.png')
plt.show()
print("Chart saved!")

# ── Budget variance ────────────────────────────────────────────────────────────
monthly_spend = df.groupby(['month', 'category', 'budget'])['amount'] \
                  .sum().reset_index()
monthly_spend.columns = ['month', 'category', 'budget', 'spent']
monthly_spend['variance'] = monthly_spend['budget'] - monthly_spend['spent']
monthly_spend['status'] = monthly_spend['variance'].apply(
    lambda x: 'Under budget' if x >= 0 else 'Over budget'
)

print("\n── Budget variance (last month) ──")
last_month = monthly_spend[monthly_spend['month'] == monthly_spend['month'].max()]
print(last_month[['category', 'budget', 'spent', 'variance', 'status']].to_string(index=False))

# ── Monthly trend ──────────────────────────────────────────────────────────────
monthly_total = df.groupby('month')['amount'].sum()

plt.figure(figsize=(12, 5))
monthly_total.plot(kind='line', marker='o', color='steelblue', linewidth=2)
plt.title('Monthly Spending Trend')
plt.ylabel('Total Spend ($)')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/monthly_trend.png')
plt.show()
print("Trend chart saved!")

# ── NumPy statistics ───────────────────────────────────────────────────────────
amounts = df['amount'].values  # convert to NumPy array

print("\n── Spending statistics ──")
print(f"Mean transaction:   ${np.mean(amounts):.2f}")
print(f"Median transaction: ${np.median(amounts):.2f}")
print(f"Std deviation:      ${np.std(amounts):.2f}")
print(f"Largest purchase:   ${np.max(amounts):.2f}")
print(f"Smallest purchase:  ${np.min(amounts):.2f}")

# Transactions more than 2 standard deviations above the mean
threshold = np.mean(amounts) + 2 * np.std(amounts)
large_transactions = df[df['amount'] > threshold]
print(f"\nTransactions over ${threshold:.2f} (2σ): {len(large_transactions)}")
print(large_transactions[['date', 'amount', 'merchant', 'category']].head(10))

# ── Top merchants ──────────────────────────────────────────────────────────────
top_merchants = df.groupby('merchant')['amount'].sum().sort_values(ascending=False).head(10)

print("\n── Top 10 merchants by spend ──")
print(top_merchants.round(2))

plt.figure(figsize=(10, 5))
sns.barplot(x=top_merchants.values, y=top_merchants.index, palette='Oranges_d')
plt.title('Top 10 Merchants by Total Spend')
plt.xlabel('Amount ($)')
plt.tight_layout()
plt.savefig('data/top_merchants.png')
plt.show()
print("Merchant chart saved!")

