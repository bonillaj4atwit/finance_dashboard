import sqlite3
import pandas as pd

conn = sqlite3.connect('data/finance.db')

df = pd.read_sql_query('''
    SELECT 
        t.date,
        t.amount,
        m.name AS merchant,
        c.name AS category,
        c.budget,
        t.description
    FROM transactions t
    JOIN merchants m ON t.merchant_id = m.id
    JOIN categories c ON m.category_id = c.id
    ORDER BY t.date
''', conn)

conn.close()

df['date'] = pd.to_datetime(df['date'])

print(df.head(10))
print(f"\nShape: {df.shape}")
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
print(f"\nCategories: {df['category'].unique()}")