import pyodbc
import os

def run_migrations():
    # Connection parameters
    server = "111.93.26.122"
    database = "voicebot"
    username = "sa"
    password = "Oliva@9876"
    
    # Create connection string
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )
    
    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Read and execute the organizations table creation script
        with open('app/db/migrations/create_organizations_table.sql', 'r') as file:
            sql_script = file.read()
            cursor.execute(sql_script)
            conn.commit()
        
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migrations() 