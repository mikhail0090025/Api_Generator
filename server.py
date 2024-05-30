from flask import Flask, request, jsonify, send_from_directory
from pydanticModels import process_models
from apiCreator import create_api
import os
from main import get_database_info, host, user, password, main, create_database

app = Flask(__name__)

def list_to_string(items):
    """
    Converts a list of items into a string with each item separated by a newline.

    Arguments:
    items (list): The list of items to be converted.

    Returns:
    str: A string with each item separated by a newline.
    """
    result = ""
    for item in items:
        result += item
        result += "\n"
    return result

@app.route('/sql_code', methods=['POST'])
def sql_code():
    given_data = request.json
    given_sql_code = given_data['sql_code']
    given_db_name = given_data['db_name']

    if given_sql_code is None:
        return jsonify({"error": "No JSON data provided"}), 400

    api = ""
    # Get the directory of the current file
    current_directory = os.path.dirname(__file__)
    # Join the directory path with the filename
    api_file_path = os.path.join(current_directory, 'crud_api.py')
    with open(api_file_path) as file:
        # Read the entire content of the file crud_api.py
        api = file.read()
    
    # Database info
    ggg = main(host, user, password, given_db_name, given_sql_code)
    print("ggg")
    print(ggg)
    print("ggg")
    db_info = get_database_info(host, user, password, given_db_name)

    '''
        #get APIs
        code = ""
        with open(given_db_name + "crud_api.py") as file:
            code = file.read()

        def get_lines_starting_with_at(file_content):
            # Split the content into lines
            lines = file_content.splitlines()
            
            # Filter lines that start with '@'
            at_lines = [line for line in lines if line.startswith('@')]
            
            return at_lines
        
        api_lines = get_lines_starting_with_at(code)
        print(api_lines)
    '''
    # Return a JSON response
    return jsonify({"sql_code": given_sql_code, "api": api, "db_info": db_info}), 200
    #return jsonify({"sql_code": given_sql_code, "api": api, "db_info": list_to_string(db_info[0])}), 200

@app.route('/', methods=['GET'])
def default_endpoint():
    return send_from_directory("frontend", "index.html")

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

def start_server():
    app.run(debug=True)