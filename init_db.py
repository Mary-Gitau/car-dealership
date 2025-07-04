import sqlite3

conn = sqlite3.connect('carzone.db')
cursor = conn.cursor()

# Drop old car table (optional if you're starting fresh)
cursor.execute('DROP TABLE IF EXISTS car')

# Create new car table with year and brand
cursor.execute('''
CREATE TABLE car (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    year INTEGER NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database reset: 'car' table with brand and year created.")

