import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "app"))
from app.config import SqlPostgres
import psycopg2
from psycopg2 import sql
import psycopg2.extras 
import logging

log_file_path = os.path.join(project_root, 'app.log')

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UploaderSql:
    def __init__(self):
        db = SqlPostgres()
        self.connection = db.connect()

    def _execute_query(self, query, params=None):
        """Helper function to execute queries safely."""
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                self.connection.commit()
            except psycopg2.Error as e:
                logging.error(f"Database error: {e}")
                self.connection.rollback()

    def data_exists(self, table, condition_column, condition_value):
        """
        Checks if data matching the condition already exists in the table.
        """
        query = sql.SQL("SELECT 1 FROM {} WHERE {} = %s LIMIT 1").format(
            sql.Identifier(table),
            sql.Identifier(condition_column)
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query, (condition_value,))
            return cursor.fetchone() is not None

    def insert_into_table(self, table, data, column_map, batch_size=1000):
        """
        Inserts data into the table in batches, skipping if a condition is met.

        Args:
            table (str): The table name.
            data (list of list): The data to insert.
            column_map (dict): A mapping of column names to keys in `data`.
            batch_size (int): The number of rows to insert per batch.
        """
        condition_column, _ = next(iter(column_map.items()))

        columns = list(column_map.keys())
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]

        for batch in batches:
            values_list = []
            for row in batch:
                values = [row[column_map[col]] for col in columns]

                # Check for blank or null values
                if any(val in (None, '', 'NULL') for val in values):
                    continue

                if not self.data_exists(table, condition_column, values[0]):
                    values_list.append(values)

            if values_list:
                insert_query = sql.SQL("""
                    INSERT INTO {} ({}) 
                    VALUES {}
                    ON CONFLICT DO NOTHING;
                """).format(
                    sql.Identifier(table),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.SQL("({})").format(
                        sql.SQL(', ').join(sql.Placeholder() * len(columns))
                    ) for _ in values_list)
                )
                flattened_values = [item for sublist in values_list for item in sublist]
                self._execute_query(insert_query, flattened_values)
                logging.info(f"Batch of data uploaded to table {table}")

    def get_column_map(self, table_name):
        """
        Retrieves a dictionary mapping column names to their positions for a given table.
        """
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s;
        """
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, (table_name,))
            columns = cursor.fetchall()

        # Create the column_map: column_name -> index in data row
        column_map = {col['column_name']: i for i, col in enumerate(columns)}
        return column_map
