from pydantic import BaseModel, Field #type: ignore
from fastapi import FastAPI, HTTPException #type: ignore
import importlib.util
from typing import List
import os 

def create_api(pydantic_script, database_name):
    """
    Creates crud_api.py script with all CRUD methods

    Arguments:
        `pydantic_script` (str): Models script name.
    Returns:    
        (str): Name of created api script.
    """
    models = load_pydantic_models(pydantic_script)
    models_names = ", ".join([model.__name__ for model in models])

    converted_pydantic_script_string = pydantic_script.replace("\\", ".")
    #import
    script = """from fastapi import FastAPI, HTTPException\n"""
    script += """from datetime import datetime, timedelta\n"""
    script += """from decimal import Decimal\n"""
    script += f"""from {converted_pydantic_script_string[:-3]} import {models_names}\n"""
    script += """import mysql.connector\napp = FastAPI()\n\n"""
    #db params
    script += """db_config = {\n"""
    script += """\t'host': 'localhost',\n"""
    script += """\t'user': 'root',\n"""
    script += """\t'password': '',\n"""
    script += """\t'database': 'newdb'\n}\n\n"""
    #sql query function
    script += """def execute_query(query, params=None):\n"""
    script += """\ttry:\n"""
    script += """\t\tconnection = mysql.connector.connect(**db_config)\n"""
    script += """\t\tcursor = connection.cursor()\n\n"""
    script += """\t\tif params:\n"""
    script += """\t\t\tcursor.execute(query, params)\n"""
    script += """\t\telse:\n"""
    script += """\t\t\tcursor.execute(query)\n\n"""
    script += """\t\tresult = cursor.fetchall()\n\n"""
    script += """\t\tcursor.close()\n"""
    script += """\t\tconnection.commit()\n"""
    script += """\t\tconnection.close()\n\n"""
    script += """\t\treturn result\n\n"""
    script += """\texcept mysql.connector.Error as err:\n"""
    script += """\t\traise HTTPException(status_code=500, detail=f"Database error: {err}")\n\n"""

    for model in models:
        script += create(model)
        script += read(model)
        script += update(model)
        script += delete(model)
    
    #write into new script
    directory = "crud_api"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    api_script_name = os.path.join(directory, f"{database_name}_crud_api.py")

    with open(api_script_name, "w") as file:
        file.write(script)

    print(f'Endpoints "{api_script_name}" successfully created.')

    return api_script_name

def load_pydantic_models(pydantic_script) -> List[BaseModel]:
    """
    Returns all pydantic models from script.

    Arguments:
        `pydantic_script` (str): Models script name.
    Returns:
        List of models.
    """
    spec = importlib.util.spec_from_file_location("module_name", pydantic_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    models = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj != BaseModel:
            models.append(obj)
    return models

def create(model):
    """
    Creates string for post method

    Arguments:
        `model`: Pydantic model.
    Returns:
        str: Post method script.
    """

    #Get Primary Key
    primary_key_name = None
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break
    
    #Get variables
    variables = []
    variables_names = []
    #in format {var_name} = {model_name}.{var_name} like
    #   name = car.name
    variables_formated = []
    for field_name, field_type in model.__annotations__.items():
        if field_name != primary_key_name:
            type_name = field_type.__name__
            variables.append(f"{field_name}: {type_name}")
            variables_names.append(field_name)
            variables_formated.append(field_name + ' = ' + model.__name__ + '.' + field_name)

    #Route + function
    string = f"""@app.post("/{model.__name__}/") \n"""
    string += f"""async def create_{model.__name__}({model.__name__}: {model.__name__}):\n"""

    #Comments
    string += """\t'''\n"""
    string += f"""\tCreate {model.__name__} \n"""
    string += """\tArgument: \n"""
    string += f"""\t\t{model.__name__}: {model.__name__}: An object, representing model.\n"""
    string += """\t'''\n"""

    #Function body
    #SQL query
    string += """\n"""
    string += """\ttry:\n"""
    string += "\t\t{}\n".format('\n\t\t'.join(variables_formated))
    string += """\t\tquery = '''\n"""
    string += f"""\t\tINSERT INTO {model.__name__} ({', '.join(variables_names)})\n"""
    string += f"""\t\tVALUES ({', '.join(['%s'] * len(variables_names))})\n"""
    string += """\t\t'''\n\n"""
    string += f"""\t\tparams = ({', '.join(variables_names)})\n"""
    string += """\t\texecute_query(query, params)\n\n"""
    string += f"""\t\treturn {{'message': '{model.__name__} successfully created'}}\n\n"""
    string += """\texcept mysql.connectore.Error as e:\n"""
    string += """\t\traise HTTPException(status_code=500, detail=str(e))\n\n"""

    return string

def read(model):
    """
    Creates string for get method

    Arguments:
        `model`: Pydantic model.
    Returns:
        str: Get method string.
    """
    #Get Primary Key
    primary_key_name = None
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break

    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.get("/{model.__name__}/{primary_key_name_str}") \n"""
        string += f"""async def read_{model.__name__}("""
        string += f"""{primary_key_name}: int = None"""  
    else: 
        string = f"""@app.get("/{model.__name__}/None") \n"""
        string += f"""async def read_{model.__name__}("""

    string += """):\n"""

    #Check for all variables
    variables = []
    variables_names = []
    for field_name, field_type in model.__annotations__.items():
        if field_name != primary_key_name:
            type_name = field_type.__name__
            variables.append(f"{field_name}: {type_name}")
            variables_names.append(field_name)
    
    #Comments
    string += """\t'''\n"""
    string += f"""\tReturn {model.__name__} \n"""
    string += f"""\tArgument: \n"""
    string += f"""\t\t{primary_key_name}: int: Model id.\n"""
    string += """\t'''\n\n"""

    #Function body
    #SQL query
    string += f"""\tif not {primary_key_name}: \n"""
    string += f"""\t\tquery = 'SELECT {', '.join(variables_names)} FROM {model.__name__}'\n"""
    string += f"""\telse:\n"""
    string += f"""\t\tquery = f'SELECT {', '.join(variables_names)} FROM {model.__name__} WHERE {primary_key_name} = """
    string += "{"
    string += f"{primary_key_name}"
    string += "}'\n"
    string += """\tresult = execute_query(query)\n\n"""
    string += """\t#check if deleted\n\tfiltered_result = [record for record in result if record['IsActive']]\n\n"""
    string += """\tif result:\n"""
    string += """\t\treturn {'data': result}\n""" 
    string += """\telse:\n"""
    string += """\t\traise HTTPException(status_code=404, detail='Data not found')\n\n"""

    return string

def update(model):
    """
    Creates string for put method

    Arguments:
        `model`: Pydantic model.
    Returns:
        str: Put method string.
    """
    #Get Primary Key
    primary_key_name = ''
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break
    
    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.put("/{model.__name__}/{primary_key_name_str}") \n"""
        string += f"""async def update_{model.__name__}("""
    else: 
        string = f"""@app.put("/{model.__name__}/None") \n"""
        string += f"""async def update_{model.__name__}("""
    
    #Check for all variables
    variables = []
    variables_names = []
    variables_formated = []
    for field_name, field_type in model.__annotations__.items():
        if field_name != primary_key_name:
            type_name = field_type.__name__
            variables.append(f"{field_name}: {type_name}")
            variables_names.append(field_name)
            variables_formated.append(field_name + ' = %s')

    string += f"""{primary_key_name}, {", ".join(variables)}"""
    string += """):\n"""

    #Comments
    string += """\t'''\n"""
    string += f"""\tEdit {model.__name__} \n"""
    string += """\tArgument: \n"""
    string += "\t\t{}\n".format('\n\t\t'.join(variables))
    string += """\t'''\n\n"""

    #Function body
    #SQL query
    string += """\ttry:\n"""
    string += f"""\t\t{model.__name__}_exists_query = 'SELECT * FROM {model.__name__} WHERE {primary_key_name} = %s'\n"""
    string += f"""\t\t{model.__name__}_exists_params = ({primary_key_name})\n"""
    string += f"""\t\t{model.__name__}_exists_result = execute_query({model.__name__}_exists_query, {model.__name__}_exists_params)\n\n"""
    string += f"""\t\tif {model.__name__}_exists_result == False:\n"""
    string += f"""\t\t\traise HTTPException(status_code=404, defail=f"{model.__name__} with ID {primary_key_name} not found")\n\n"""
    string += f"""\t\tif {model.__name__}_exists_result[0]['IsActive'] == 0:\n"""
    string += f"""\t\t\traise HTTPException(status_code=403, detail="Cannot update inactive records")\n\n"""
    string += """\t\tupdate_query = '''\n"""
    string += f"""\t\tIPDATE {model.__name__}\n"""
    string += f"""\t\tSET {', '.join(variables_formated)}\n"""
    string += f"""\t\tWHERE {primary_key_name} = %s\n"""
    string += """\t\t'''\n\n"""
    string += f"""\t\tupdate_params = ({', '.join(variables_names)})\n"""
    string += """\t\texecute_query(update_query, update_params)\n\n"""
    string += f"""\t\treturn {{"message": f"{model.__name__} with ID {primary_key_name} successfully updated"}}\n"""
    string += """\texcept mysql.connector.Error as e:\n"""
    string += """\t\traise HTTPException(status_code=500, dateil=str(e))\n"""
    
    string += f"""\n"""

    return string
    
def delete(model):
    """
    Creates string for delete method

    Arguments:
        `model`: Pydantic model.
    Returns:
        str: Delete method string.
    """
    #Get Primary Key
    primary_key_name = None
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break

    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.delete("/{model.__name__}/{primary_key_name_str}") \n"""
        string += f"""async def delete_{model.__name__}("""
        string += f"""{primary_key_name}: int"""  
    else: 
        string = f"""@app.delete("/{model.__name__}/None") \n"""
        string += f"""async def delete_{model.__name__}("""

    string += """):\n"""

    #Comments
    string += f"""\t'''\n"""
    string += f"""\tDeactivate {model.__name__} \n"""
    string += f"""\tArgument: \n"""
    string += f"""\t\t{primary_key_name}: int: Model id.\n"""
    string += """\t'''\n\n"""

    #Function body
    #SQL query
    string += """\ttry:\n"""
    string += f"""\t\t{model.__name__}_exists_query = 'SELECT IsActive FROM {model.__name__} WHERE {primary_key_name} = %s'\n"""
    string += f"""\t\t{model.__name__}_exists_params = ({primary_key_name},)\n"""
    string += f"""\t\t{model.__name__}_exists_result = execute_query({model.__name__}_exists_query, {model.__name__}_exists_params)\n\n"""
    string += f"""\t\tif not {model.__name__}_exists_result:\n"""
    string += f"""\t\t\traise HTTPException(status_code=404, detail=f"{model.__name__} with ID {primary_key_name} not found")\n\n"""
    string += f"""\t\tif {model.__name__}_exists_result[0]['IsActive'] == 0:\n"""
    string += f"""\t\t\treturn {{"message": f"{model.__name__} with ID {primary_key_name} is already inactive"}}\n\n"""
    string += f"""\t\tupdate_query = 'UPDATE {model.__name__} SET IsActive = 0 WHERE {primary_key_name} = %s'\n"""
    string += f"""\t\tupdate_params = ({primary_key_name},)\n"""
    string += """\t\texecute_query(update_query, update_params)\n\n"""
    string += f"""\t\treturn {{"message": f"{model.__name__} with ID {primary_key_name} successfully deactivated"}}\n"""
    string += """\texcept mysql.connector.Error as e:\n"""
    string += """\t\traise HTTPException(status_code=500, detail=str(e))\n"""
    string += """\n"""

    return string
"""
try:
        # Check if the car exists and its IsActive status
        car_exists_query = 'SELECT IsActive FROM cars WHERE CarID = %s'
        car_exists_params = (CarID,)
        car_exists_result = execute_query(car_exists_query, car_exists_params)

        if not car_exists_result:
            raise HTTPException(status_code=404, detail=f"Car with ID {CarID} not found")

        if car_exists_result[0]['IsActive'] == 0:
            return {"message": f"Car with ID {CarID} is already inactive"}

        # Update the car to set IsActive to false
        update_query = 'UPDATE cars SET IsActive = 0 WHERE CarID = %s'
        update_params = (CarID,)
        execute_query(update_query, update_params)

        return {"message": f"Car with ID {CarID} successfully deactivated"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
    