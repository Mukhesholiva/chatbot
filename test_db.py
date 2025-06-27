import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=183.82.126.21;"
    "DATABASE=voicebot;"
    "UID=sa;"
    "PWD=Oliva@9876;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Connection successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT @@version")
    row = cursor.fetchone()
    print(f"SQL Server version: {row[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {str(e)}") 