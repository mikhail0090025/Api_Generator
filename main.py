import mysql.connector # type: ignore 
from pydantic import BaseModel, Field # type: ignore 
from typing import List 
import time 
import json 
from pydanticModels import process_models 
from apiCreator import create_api
import server

if __name__ == "__main__":
    server.start_server()
def create_database(host, user, password, database_name, sql_code: str): 
    """ 
    Creates database. 
 
    Arguments: 
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Name of database. 
        sql_code (str): Code for database creation. 
    Returns: 
        1: Success. 
        0: Fail. 
    """ 
    connection = mysql.connector.connect( 
        host=host, 
        user=user, 
        password=password 
        ) 
     
    if connection.is_connected(): 
        cursor = connection.cursor() 
        #print(type(sql_code))
        #create db 
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name}") 
        cursor.execute(f"CREATE DATABASE {database_name}") 
        cursor.execute(f"USE {database_name}") 
 
        #instead of multi=True execute each command one by one 
        sql_commands = sql_code.strip().split(';') 
        for command in sql_commands: 
            if command.strip(): 
                cursor.execute(command + ';') 
        #cursor.execute(sql_code, multi=True) 
        #cursor.execute(f"USE {database_name}") 
 
        print(f'Database "{database_name}" successfully created.') 
        cursor.close() 
        connection.close() 
        return 1 
    else: 
        print('Unable to connect to db.') 
        return 0 
 
def get_database_info(host, user, password, database_name): 
    """ 
    Returns information about all tables in database. 
 
    Arguments: 
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Database name. 
    Return: 
        Dics/List: List of strings with database descriptions. 
        Int: Count of tables. 
    """ 
    time.sleep(0.1) 
    connection = mysql.connector.connect( 
        host=host, 
        user=user, 
        password=password, 
        database=database_name   
    ) 
     
    cursor = connection.cursor() 
     
    cursor.execute("SHOW TABLES") 
    tables = cursor.fetchall() 
    table_count = len(tables) 
    table_descriptions = {} 
     
    for (table_name,) in tables:
        #get info about table
        cursor.execute(f"DESCRIBE {table_name}")
        description = cursor.fetchall()
        table_descriptions[table_name] = description
 
    cursor.close() 
    connection.close() 
 
    return table_descriptions, table_count 
 
def format_database(host, user, password, database_name): 
    """ 
    Adds into db IsActive column. 
 
    Arguments: 
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Database name. 
    """ 
    time.sleep(0.1) 
    connection = mysql.connector.connect( 
        host=host, 
        user=user, 
        password=password, 
        database=database_name   
    ) 
     
    cursor = connection.cursor() 
     
    cursor.execute("SHOW TABLES") 
    tables = cursor.fetchall() 
    table_count = len(tables) 
    table_descriptions = {} 
     
    for (table_name,) in tables:
        #add IsActive column to tables
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN IsActive BOOLEAN DEFAULT TRUE")
 
    cursor.close() 
    connection.close() 
 
    return
 
def format_sql_code(database_name, sql_code_body): 
    """ 
    Returns formated sql code. 
 
    Arguments: 
        database_name (str): Name of db. 
        sql_code_body (str): Db code. 
    Returns: 
        Str: Formated sql code. 
    """ 
    if any(line.strip().startswith(("CREATE DATABASE", "USE")) for line in sql_code_body.strip().split('\n')): 
        sql_code_body = [line for line in sql_code_body.strip().split('\n') if not line.strip().startswith(("CREATE DATABASE", "USE"))] 
        sql_code_body = '\n'.join(sql_code_body) 
     
    return sql_code_body
 
host = 'localhost' 
user = 'root' 
password = '' 
database_name = 'newdb' 
 
sql_code_body = """ 

 
 
-- Create the Manufacturers table 
CREATE TABLE Manufacturers ( 
    ManufacturerID INT AUTO_INCREMENT PRIMARY KEY, 
    Name VARCHAR(255) NOT NULL, 
    Country VARCHAR(255) NOT NULL, 
    FoundedYear INT 
); 
 
-- Create the Models table 
CREATE TABLE Models ( 
    ModelID INT AUTO_INCREMENT PRIMARY KEY, 
    ManufacturerID INT NOT NULL, 
    Name VARCHAR(255) NOT NULL, 
    Year INT NOT NULL, 
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID) 
); 
 
-- Create the Dealerships table 
CREATE TABLE Dealerships ( 
    DealershipID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL, 
    Location VARCHAR(255) NOT NULL, 
    ContactNumber VARCHAR(20) 
); 
 
-- Create the Cars table 
CREATE TABLE Cars ( 
    CarID INT AUTO_INCREMENT PRIMARY KEY, 
    ModelID INT NOT NULL, 
    DealershipID INT NOT NULL, 
    VIN VARCHAR(17) NOT NULL UNIQUE, 
    Price DECIMAL(10, 2) NOT NULL, 
    Status ENUM('Available', 'Sold', 'Servicing') NOT NULL, 
    FOREIGN KEY (ModelID) REFERENCES Models(ModelID), 
    FOREIGN KEY (DealershipID) REFERENCES Dealerships(DealershipID) 
); 
 
-- Create the Customers table 
CREATE TABLE Customers ( 
    CustomerID INT AUTO_INCREMENT PRIMARY KEY, 
    FirstName VARCHAR(255) NOT NULL, 
    LastName VARCHAR(255) NOT NULL, 
    Email VARCHAR(255) NOT NULL UNIQUE, 
    PhoneNumber VARCHAR(20), 
    Address TEXT 
); 
 
-- Create the Sales table 
CREATE TABLE Sales ( 
    SaleID INT AUTO_INCREMENT PRIMARY KEY, 
    CarID INT NOT NULL, 
    CustomerID INT NOT NULL, 
    SaleDate DATE NOT NULL, 
    SalePrice DECIMAL(10, 2) NOT NULL, 
    FOREIGN KEY (CarID) REFERENCES Cars(CarID), 
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) 
); 
 
-- Create the ServiceRecords table 
CREATE TABLE ServiceRecords ( 
    ServiceID INT AUTO_INCREMENT PRIMARY KEY, 
    CarID INT NOT NULL, 
    ServiceDate DATE NOT NULL, 
    Description TEXT NOT NULL, 
    Cost DECIMAL(10, 2), 
    FOREIGN KEY (CarID) REFERENCES Cars(CarID) 
); 
 
""" 
 
def main(host, user, password, database_name, sql_code_body: str): 
    #db creation 
    sql_code = sql_code_body#= format_sql_code(database_name, sql_code_body)
    
    create_database(host, user, password, database_name, sql_code) 
 
    #get db info + format into json 

    format_database(host, user, password, database_name)
    db_info, depth = get_database_info(host, user, password, database_name) 
    db_info_json = json.dumps(db_info, indent=depth) 
    #print(db_info_json) 
 
    pydantic_script = process_models(db_info_json, database_name)
    endpoints_script = create_api(pydantic_script, database_name)

    return endpoints_script

main(host, user, password, database_name, sql_code_body)