from sqlalchemy import inspect
from .session import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables():
    """Check what tables exist in the database and their columns."""
    inspector = inspect(engine)
    
    # Get all table names
    table_names = inspector.get_table_names()
    logger.info(f"Found tables: {table_names}")
    
    # For each table, get column information
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        logger.info(f"\nTable: {table_name}")
        for column in columns:
            logger.info(f"Column: {column['name']}, Type: {column['type']}")

if __name__ == "__main__":
    check_tables() 