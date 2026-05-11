import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
conn = sqlite3.connect('data/finance.db')
cursor = conn.cursor()

# Seed categories with monthly budgets
categories = [
    ('Groceries', 400),
    ('Dining', 200),
    ('Transport', 150),
    ('Entertainment', 100),
    ('Utilities', 200),
    ('Shopping', 300),
    ('Health', 100),
]

cursor.executemany(
    'INSERT INTO categories (name, budget) VALUES (?, ?)', categories
)

# Seed merchants per category
merchants = [
    ('Whole Foods', 1), ('Trader Joes', 1), ('Kroger', 1),
    ('Chipotle', 2), ('Starbucks', 2), ('McDonalds', 2),
    ('Uber', 3), ('Shell Gas', 3), ('Delta Airlines', 3),
    ('Netflix', 4), ('Spotify', 4), ('AMC Theaters', 4),
    ('Duke Energy', 5), ('AT&T', 5), ('Water Dept', 5),
    ('Amazon', 6), ('Target', 6), ('Nike', 6),
    ('CVS Pharmacy', 7), ('Gym Membership', 7),
]

cursor.executemany(
    'INSERT INTO merchants (name, category_id) VALUES (?, ?)', merchants
)

# Generate 12 months of transactions
start_date = datetime.now() - timedelta(days=365)

transactions = []
for day in range(365):
    current_date = start_date + timedelta(days=day)
    num_transactions = random.randint(1, 5)
    for _ in range(num_transactions):
        merchant_id = random.randint(1, len(merchants))
        amount = round(random.uniform(5, 200), 2)
        transactions.append((
            current_date.strftime('%Y-%m-%d'),
            amount,
            merchant_id,
            fake.sentence(nb_words=4)
        ))

cursor.executemany(
    'INSERT INTO transactions (date, amount, merchant_id, description) VALUES (?, ?, ?, ?)',
    transactions
)

conn.commit()
conn.close()
print(f"Generated {len(transactions)} transactions!")