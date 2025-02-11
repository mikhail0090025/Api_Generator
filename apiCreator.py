from pydantic import BaseModel, Field #type: ignore
from fastapi import FastAPI, HTTPException #type: ignore
import importlib.util
from typing import List

def create_api(pydantic_script):
    """
    Creates crud_api.py script with all CRUD methods

    Arguments:
        `pydantic_script` (str): Models script name.
    Returns: 
        (str): Name of created api script.
    """
    models = load_pydantic_models(pydantic_script)

    models_names = ", ".join([model.__name__ for model in models])

    #import
    script = """from fastapi import FastAPI, HTTPException\n"""
    script += """from datetime import datetime, timedelta\n"""
    script += """from decimal import Decimal\n"""
    script += f"""from {pydantic_script} import {models_names}\n"""
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
    api_script_name = "crud_api.py"

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
    string += f"""\t\t{'\n\t\t'.join(variables_formated)}\n"""
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
    string += f"""\tif {primary_key_name} == None: \n"""
    string += f"""\t\tquery = 'SELECT {', '.join(variables_names)} FROM {model.__name__}'\n"""
    string += f"""\telse:\n"""
    string += f"""\t\tquery = f'SELECT {', '.join(variables_names)} FROM {model.__name__} WHERE {primary_key_name} = """
    string += "{"
    string += f"{primary_key_name}"
    string += "}'\n"
    string += """\tresult = execute_query(query)\n\n"""
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
    for field_name, field_type in model.__annotations__.items():
        if field_name != primary_key_name:
            type_name = field_type.__name__
            variables.append(f"{field_name}: {type_name}")

    string += f"""{", ".join(variables)}"""
    string += """):\n"""

    #Comments
    string += """\t'''\n"""
    string += f"""\tEdit {model.__name__} \n"""
    string += """\tArgument: \n"""
    string += f"""\t\t{'.\n\t\t'.join(variables)}.\n""" 
    string += """\t'''\n\n"""

    #Function body
    #SQL query
    string += """\ttry:\n"""
    string += f"""\t\t{model.__name__}_exists_query = 'SELECT * FROM {model.__name__} WHERE {primary_key_name} = %s'\n"""
    string += f"""\t\t{model.__name__}_exists_params = ({primary_key_name})\n"""
    string += f"""\t\t{model.__name__}_exists_result = exceture_query({model.__name__}_exists_query, {model.__name__}_exists_params)\n\n"""
    string += f"""\t\tif no {model.__name__}_exists_result:\n"""
    string += f"""\t\t\traise HTTPException(status_code=404, defail=f"{model.__name__} with ID {primary_key_name} not found")\n\n"""
    string += f"""\t\tupdate_query = '''"""
    """
    try:
        car_exists_query = "SELECT * FROM Cars WHERE CarID = %s"
        car_exists_params = (CarID,)
        car_exists_result = execute_query(car_exists_query, car_exists_params)

        if not car_exists_result:
            raise HTTPException(status_code=404, detail=f"Car with ID {CarID} not found")

        update_query = '''
        UPDATE Cars
        SET ModelID = %s, DealershipID = %s, VIN = %s, Price = %s, Status = %s
        WHERE CarID = %s
        '''
        update_params = (ModelID, DealershipID, VIN, Price, Status, CarID)
        execute_query(update_query, update_params)

        # Формируем JSON-ответ
        return {"message": f"Car with ID {CarID} successfully updated"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    """
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
    string += f"""\n"""

    return string