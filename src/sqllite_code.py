import sqlite3

# Connect to a local SQLite database (or create one if it doesn't exist)
conn = sqlite3.connect("my_database.db")
cursor = conn.cursor()

# Create a table
cursor.execute("""
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT,
    address TEXT,
    locality TEXT,
    region TEXT,
    postal_code TEXT,
    country TEXT
)
""")

# Insert data
cursor.execute("INSERT INTO companies (company_id, company_name) VALUES (?, ?)", ("1", "ABC Pharma"))
conn.commit()

# Query data
cursor.execute("SELECT * FROM companies")
print(cursor.fetchall())

conn.close()
