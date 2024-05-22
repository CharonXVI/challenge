from dotenv import load_dotenv
import psycopg2
import logging
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log_file_path = os.path.join(project_root, 'app.log')

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv(r"app\DB_URL.env")

class SqlPostgres:
    def __init__(self):
        self.host = os.environ.get("host")
        self.database = os.environ.get("database")
        self.user = os.environ.get("user")
        self.password = os.environ.get("password")
        self._connection = None

    def connect(self):
        try:
            self._connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logging.info("Connection established successfully to the database.")
            return self._connection
        except psycopg2.Error as e:
            logging.info(f"Error connecting to the database: {e}")
            raise  

    def close(self):
        if self._connection:
            self._connection.close()
            logging.info("Database connection closed.")

