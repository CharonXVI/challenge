import sys
import os
import logging
from psycopg2 import sql, OperationalError, ProgrammingError

# Assuming the classes are located in these paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "tables_globant"))
sys.path.append(os.path.join(project_root, "app"))

from tables_globant.department import Department
from tables_globant.jobs import Job
from tables_globant.employee import Employee
from app.config import SqlPostgres

# Initialize logging
log_file_path = os.path.join(project_root, 'app.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TableCreator:
    def __init__(self):
        db = SqlPostgres()
        self.connection = db.connect()

        # Map table names to their respective queries
        self.table_queries = {
            Department.table_name: Department.query,
            Job.table_name: Job.query,
            Employee.table_name: Employee.query
        }

    def create_table(self, table_name):
        """
        Create table based on the provided table name.
        """
        table_query = self.table_queries.get(table_name)

        if not table_query:
            raise ValueError(f"Invalid table name: {table_name}")

        with self.connection.cursor() as cursor:
            try:
                logging.info(f"Creating table {table_name}")
                create_table_query = sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} ("
                    "{}"
                    ");"
                ).format(
                    sql.Identifier(table_name),
                    sql.SQL(",").join(map(sql.SQL, table_query.split(",")))
                )
                cursor.execute(create_table_query)
                self.connection.commit()
                logging.info(f"Creating table {table_name} successful")
            except (OperationalError, ProgrammingError) as e:
                logging.error(f"Error creating table {table_name}: {e}")
                self.connection.rollback()
            except Exception as e:
                logging.error(f"Unexpected error creating table {table_name}: {e}")
                self.connection.rollback()
            finally:
                logging.info(f"Creating table {table_name} completed - closing connection")
                
    def close_connection(self):
        """Close the connection when all tables have been created."""
        if self.connection:  # Check if connection exists
            logging.info(f"Closing connection")
            self.connection.close()
            logging.info("Connection closed")