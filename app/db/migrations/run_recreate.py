import os
import pyodbc
from ...core.config import settings

def run_recreate():
    # Build connection string
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_NAME};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Read and execute the SQL script
        migration_file = os.path.join(os.path.dirname(__file__), 'recreate_users_table.sql')
        with open(migration_file, 'r') as file:
            sql_script = file.read()
            
            # Split the script into individual statements
            statements = sql_script.split(';')
            
            # Execute each statement
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
                    conn.commit()

        print("Table recreation completed successfully!")
        
    except Exception as e:
        print(f"Error during table recreation: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_recreate() 