import sqlite3

conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

# Get profiles table schema
cursor.execute("PRAGMA table_info(profiles)")
columns = cursor.fetchall()

print("\nTable: profiles")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close() 