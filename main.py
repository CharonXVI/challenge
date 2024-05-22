from flask import Flask, request, jsonify
import sys
sys.path.append(r".\services")
from flasgger import Swagger  
from services.create_table import TableCreator
from services.csv_parser import parse_csv
from services.uploader import UploaderSql
from tables import create_tables_in_order
from flask_cors import CORS
import logging

app = Flask(__name__)
swagger = Swagger(app)  
CORS(app)

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
table_creator = TableCreator()
tables = ["department", "job", "employee"]
create_tables_in_order(table_creator, tables)
uploader = UploaderSql()



@app.route('/migrate', methods=['POST'])
def migrate_data():
    """
    Migrate data from CSV file to database.
    ---
    tags:
      - Migration
    consumes:
      - multipart/form-data
    parameters:
      - name: csv_file
        in: formData
        type: file
        required: true
        description: The CSV file to upload.
    responses:
      200:
        description: Migration successful.
      400:
        description: Bad Request - Missing or invalid CSV file.
      500:
        description: Internal Server Error - Migration failed.
    """
    if 'csv_file' not in request.files:
        return jsonify({"error": "Missing CSV file"}), 400

    csv_file = request.files['csv_file']

    try:
        recognized_name, data = parse_csv(csv_file)
        recognized_name=recognized_name.lower()
        table_creator.create_table(recognized_name)
        column_map = uploader.get_column_map(recognized_name)
        uploader.insert_into_table(recognized_name, data, column_map)
        return jsonify({"message": "Migration successful!"}), 200
    except Exception as e:
        app.logger.error(f'Migration failed: {e}')
        return jsonify({"error": f"Migration failed: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)

