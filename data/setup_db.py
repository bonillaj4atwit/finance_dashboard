import sqlite3

conn = sqlite3.connect('data/finance.db')
cursor = conn.cursor()

cursor.executescript('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        budget REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        merchant_id INTEGER,
        description TEXT,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
''')

conn.commit()
conn.close()
print("Database created successfully!")