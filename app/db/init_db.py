import pyodbc
from ..core.config import settings

def init_db():
    # Create connection string
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_NAME};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD}"
    )
    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # Read and execute the SQL file batch by batch (split on GO)
        with open('app/db/init.sql', 'r') as sql_file:
            sql_commands = sql_file.read()
            batches = [batch.strip() for batch in sql_commands.split('GO') if batch.strip()]
            for batch in batches:
                cursor.execute(batch)
            conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_db()

def drop_db() -> None:
    """Drop all tables."""
    try:
        print("Dropping database tables...")
        # Create connection string
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={settings.DB_SERVER};"
            f"DATABASE={settings.DB_NAME};"
            f"UID={settings.DB_USER};"
            f"PWD={settings.DB_PASSWORD}"
        )
        
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Read and execute the SQL file batch by batch (split on GO)
        with open('app/db/init.sql', 'r') as sql_file:
            sql_commands = sql_file.read()
            batches = [batch.strip() for batch in sql_commands.split('GO') if batch.strip()]
            for batch in batches:
                cursor.execute(batch)
            conn.commit()
        print("Database tables dropped successfully!")
    except Exception as e:
        print(f"Error dropping database tables: {str(e)}")
        raise 