import sys
import os
import logging
from psycopg2 import sql, OperationalError, ProgrammingError

# Add the services directory to the path
sys.path.append(r".\services")

from services.create_table import TableCreator

# Initialize logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the TableCreator
#table_creator = TableCreator()

# Define the order of table creation
#tables = ["Department", "Job", "Employee"]

def create_tables_in_order(table_creator, tables):
    table_creator = TableCreator()
    for table_name in tables:
        try:
            table_creator.create_table(table_name.lower())  # Ensure table names are lowercase
            print(f"Successfully created table: {table_name}")
            logging.info(f"Successfully created table: {table_name}")
        except Exception as e:
            logging.error(f"Failed to create table {table_name}: {e}")
            print(f"Failed to create table: {table_name}")
    table_creator.close_connection()



