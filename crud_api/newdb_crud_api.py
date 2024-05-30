from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from decimal import Decimal
from newdb_pydantic_models import cars, customers, dealerships, manufacturers, models, sales, servicerecords
import mysql.connector
app = FastAPI()

db_config = {
	'host': 'localhost',
	'user': 'root',
	'password': '',
	'database': 'newdb'
}

def execute_query(query, params=None):
	try:
		connection = mysql.connector.connect(**db_config)
		cursor = connection.cursor()

		if params:
			cursor.execute(query, params)
		else:
			cursor.execute(query)

		result = cursor.fetchall()

		cursor.close()
		connection.commit()
		connection.close()

		return result

	except mysql.connector.Error as err:
		raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.post("/cars/") 
async def create_cars(cars: cars):
	'''
	Create cars 
	Argument: 
		cars: cars: An object, representing model.
	'''

	try:
		ModelID = cars.ModelID
		DealershipID = cars.DealershipID
		VIN = cars.VIN
		Price = cars.Price
		Status = cars.Status
		IsActive = cars.IsActive
		query = '''
		INSERT INTO cars (ModelID, DealershipID, VIN, Price, Status, IsActive)
		VALUES (%s, %s, %s, %s, %s, %s)
		'''

		params = (ModelID, DealershipID, VIN, Price, Status, IsActive)
		execute_query(query, params)

		return {'message': 'cars successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/cars/{CarID}") 
async def read_cars(CarID: int = None):
	'''
	Return cars 
	Argument: 
		CarID: int: Model id.
	'''

	if not CarID: 
		query = 'SELECT ModelID, DealershipID, VIN, Price, Status, IsActive FROM cars'
	else:
		query = f'SELECT ModelID, DealershipID, VIN, Price, Status, IsActive FROM cars WHERE CarID = {CarID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/cars/{CarID}") 
async def update_cars(CarID, ModelID: int, DealershipID: int, VIN: str, Price: Decimal, Status: str, IsActive: int):
	'''
	Edit cars 
	Argument: 
		ModelID: int
		DealershipID: int
		VIN: str
		Price: Decimal
		Status: str
		IsActive: int
	'''

	try:
		cars_exists_query = 'SELECT * FROM cars WHERE CarID = %s'
		cars_exists_params = (CarID)
		cars_exists_result = execute_query(cars_exists_query, cars_exists_params)

		if cars_exists_result == False:
			raise HTTPException(status_code=404, defail=f"cars with ID CarID not found")

		if cars_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE cars
		SET ModelID = %s, DealershipID = %s, VIN = %s, Price = %s, Status = %s, IsActive = %s
		WHERE CarID = %s
		'''

		update_params = (ModelID, DealershipID, VIN, Price, Status, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"cars with ID CarID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/cars/{CarID}") 
async def delete_cars(CarID: int):
	'''
	Deactivate cars 
	Argument: 
		CarID: int: Model id.
	'''

	try:
		cars_exists_query = 'SELECT IsActive FROM cars WHERE CarID = %s'
		cars_exists_params = (CarID,)
		cars_exists_result = execute_query(cars_exists_query, cars_exists_params)

		if not cars_exists_result:
			raise HTTPException(status_code=404, detail=f"cars with ID CarID not found")

		if cars_exists_result[0]['IsActive'] == 0:
			return {"message": f"cars with ID CarID is already inactive"}

		update_query = 'UPDATE cars SET IsActive = 0 WHERE CarID = %s'
		update_params = (CarID,)
		execute_query(update_query, update_params)

		return {"message": f"cars with ID CarID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers/") 
async def create_customers(customers: customers):
	'''
	Create customers 
	Argument: 
		customers: customers: An object, representing model.
	'''

	try:
		FirstName = customers.FirstName
		LastName = customers.LastName
		Email = customers.Email
		PhoneNumber = customers.PhoneNumber
		Address = customers.Address
		IsActive = customers.IsActive
		query = '''
		INSERT INTO customers (FirstName, LastName, Email, PhoneNumber, Address, IsActive)
		VALUES (%s, %s, %s, %s, %s, %s)
		'''

		params = (FirstName, LastName, Email, PhoneNumber, Address, IsActive)
		execute_query(query, params)

		return {'message': 'customers successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/{CustomerID}") 
async def read_customers(CustomerID: int = None):
	'''
	Return customers 
	Argument: 
		CustomerID: int: Model id.
	'''

	if not CustomerID: 
		query = 'SELECT FirstName, LastName, Email, PhoneNumber, Address, IsActive FROM customers'
	else:
		query = f'SELECT FirstName, LastName, Email, PhoneNumber, Address, IsActive FROM customers WHERE CustomerID = {CustomerID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/customers/{CustomerID}") 
async def update_customers(CustomerID, FirstName: str, LastName: str, Email: str, PhoneNumber: str, Address: str, IsActive: int):
	'''
	Edit customers 
	Argument: 
		FirstName: str
		LastName: str
		Email: str
		PhoneNumber: str
		Address: str
		IsActive: int
	'''

	try:
		customers_exists_query = 'SELECT * FROM customers WHERE CustomerID = %s'
		customers_exists_params = (CustomerID)
		customers_exists_result = execute_query(customers_exists_query, customers_exists_params)

		if customers_exists_result == False:
			raise HTTPException(status_code=404, defail=f"customers with ID CustomerID not found")

		if customers_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE customers
		SET FirstName = %s, LastName = %s, Email = %s, PhoneNumber = %s, Address = %s, IsActive = %s
		WHERE CustomerID = %s
		'''

		update_params = (FirstName, LastName, Email, PhoneNumber, Address, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"customers with ID CustomerID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/customers/{CustomerID}") 
async def delete_customers(CustomerID: int):
	'''
	Deactivate customers 
	Argument: 
		CustomerID: int: Model id.
	'''

	try:
		customers_exists_query = 'SELECT IsActive FROM customers WHERE CustomerID = %s'
		customers_exists_params = (CustomerID,)
		customers_exists_result = execute_query(customers_exists_query, customers_exists_params)

		if not customers_exists_result:
			raise HTTPException(status_code=404, detail=f"customers with ID CustomerID not found")

		if customers_exists_result[0]['IsActive'] == 0:
			return {"message": f"customers with ID CustomerID is already inactive"}

		update_query = 'UPDATE customers SET IsActive = 0 WHERE CustomerID = %s'
		update_params = (CustomerID,)
		execute_query(update_query, update_params)

		return {"message": f"customers with ID CustomerID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/dealerships/") 
async def create_dealerships(dealerships: dealerships):
	'''
	Create dealerships 
	Argument: 
		dealerships: dealerships: An object, representing model.
	'''

	try:
		Name = dealerships.Name
		Location = dealerships.Location
		ContactNumber = dealerships.ContactNumber
		IsActive = dealerships.IsActive
		query = '''
		INSERT INTO dealerships (Name, Location, ContactNumber, IsActive)
		VALUES (%s, %s, %s, %s)
		'''

		params = (Name, Location, ContactNumber, IsActive)
		execute_query(query, params)

		return {'message': 'dealerships successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/dealerships/{DealershipID}") 
async def read_dealerships(DealershipID: int = None):
	'''
	Return dealerships 
	Argument: 
		DealershipID: int: Model id.
	'''

	if not DealershipID: 
		query = 'SELECT Name, Location, ContactNumber, IsActive FROM dealerships'
	else:
		query = f'SELECT Name, Location, ContactNumber, IsActive FROM dealerships WHERE DealershipID = {DealershipID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/dealerships/{DealershipID}") 
async def update_dealerships(DealershipID, Name: str, Location: str, ContactNumber: str, IsActive: int):
	'''
	Edit dealerships 
	Argument: 
		Name: str
		Location: str
		ContactNumber: str
		IsActive: int
	'''

	try:
		dealerships_exists_query = 'SELECT * FROM dealerships WHERE DealershipID = %s'
		dealerships_exists_params = (DealershipID)
		dealerships_exists_result = execute_query(dealerships_exists_query, dealerships_exists_params)

		if dealerships_exists_result == False:
			raise HTTPException(status_code=404, defail=f"dealerships with ID DealershipID not found")

		if dealerships_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE dealerships
		SET Name = %s, Location = %s, ContactNumber = %s, IsActive = %s
		WHERE DealershipID = %s
		'''

		update_params = (Name, Location, ContactNumber, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"dealerships with ID DealershipID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/dealerships/{DealershipID}") 
async def delete_dealerships(DealershipID: int):
	'''
	Deactivate dealerships 
	Argument: 
		DealershipID: int: Model id.
	'''

	try:
		dealerships_exists_query = 'SELECT IsActive FROM dealerships WHERE DealershipID = %s'
		dealerships_exists_params = (DealershipID,)
		dealerships_exists_result = execute_query(dealerships_exists_query, dealerships_exists_params)

		if not dealerships_exists_result:
			raise HTTPException(status_code=404, detail=f"dealerships with ID DealershipID not found")

		if dealerships_exists_result[0]['IsActive'] == 0:
			return {"message": f"dealerships with ID DealershipID is already inactive"}

		update_query = 'UPDATE dealerships SET IsActive = 0 WHERE DealershipID = %s'
		update_params = (DealershipID,)
		execute_query(update_query, update_params)

		return {"message": f"dealerships with ID DealershipID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/manufacturers/") 
async def create_manufacturers(manufacturers: manufacturers):
	'''
	Create manufacturers 
	Argument: 
		manufacturers: manufacturers: An object, representing model.
	'''

	try:
		Name = manufacturers.Name
		Country = manufacturers.Country
		FoundedYear = manufacturers.FoundedYear
		IsActive = manufacturers.IsActive
		query = '''
		INSERT INTO manufacturers (Name, Country, FoundedYear, IsActive)
		VALUES (%s, %s, %s, %s)
		'''

		params = (Name, Country, FoundedYear, IsActive)
		execute_query(query, params)

		return {'message': 'manufacturers successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/manufacturers/{ManufacturerID}") 
async def read_manufacturers(ManufacturerID: int = None):
	'''
	Return manufacturers 
	Argument: 
		ManufacturerID: int: Model id.
	'''

	if not ManufacturerID: 
		query = 'SELECT Name, Country, FoundedYear, IsActive FROM manufacturers'
	else:
		query = f'SELECT Name, Country, FoundedYear, IsActive FROM manufacturers WHERE ManufacturerID = {ManufacturerID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/manufacturers/{ManufacturerID}") 
async def update_manufacturers(ManufacturerID, Name: str, Country: str, FoundedYear: int, IsActive: int):
	'''
	Edit manufacturers 
	Argument: 
		Name: str
		Country: str
		FoundedYear: int
		IsActive: int
	'''

	try:
		manufacturers_exists_query = 'SELECT * FROM manufacturers WHERE ManufacturerID = %s'
		manufacturers_exists_params = (ManufacturerID)
		manufacturers_exists_result = execute_query(manufacturers_exists_query, manufacturers_exists_params)

		if manufacturers_exists_result == False:
			raise HTTPException(status_code=404, defail=f"manufacturers with ID ManufacturerID not found")

		if manufacturers_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE manufacturers
		SET Name = %s, Country = %s, FoundedYear = %s, IsActive = %s
		WHERE ManufacturerID = %s
		'''

		update_params = (Name, Country, FoundedYear, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"manufacturers with ID ManufacturerID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/manufacturers/{ManufacturerID}") 
async def delete_manufacturers(ManufacturerID: int):
	'''
	Deactivate manufacturers 
	Argument: 
		ManufacturerID: int: Model id.
	'''

	try:
		manufacturers_exists_query = 'SELECT IsActive FROM manufacturers WHERE ManufacturerID = %s'
		manufacturers_exists_params = (ManufacturerID,)
		manufacturers_exists_result = execute_query(manufacturers_exists_query, manufacturers_exists_params)

		if not manufacturers_exists_result:
			raise HTTPException(status_code=404, detail=f"manufacturers with ID ManufacturerID not found")

		if manufacturers_exists_result[0]['IsActive'] == 0:
			return {"message": f"manufacturers with ID ManufacturerID is already inactive"}

		update_query = 'UPDATE manufacturers SET IsActive = 0 WHERE ManufacturerID = %s'
		update_params = (ManufacturerID,)
		execute_query(update_query, update_params)

		return {"message": f"manufacturers with ID ManufacturerID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/") 
async def create_models(models: models):
	'''
	Create models 
	Argument: 
		models: models: An object, representing model.
	'''

	try:
		ManufacturerID = models.ManufacturerID
		Name = models.Name
		Year = models.Year
		IsActive = models.IsActive
		query = '''
		INSERT INTO models (ManufacturerID, Name, Year, IsActive)
		VALUES (%s, %s, %s, %s)
		'''

		params = (ManufacturerID, Name, Year, IsActive)
		execute_query(query, params)

		return {'message': 'models successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{ModelID}") 
async def read_models(ModelID: int = None):
	'''
	Return models 
	Argument: 
		ModelID: int: Model id.
	'''

	if not ModelID: 
		query = 'SELECT ManufacturerID, Name, Year, IsActive FROM models'
	else:
		query = f'SELECT ManufacturerID, Name, Year, IsActive FROM models WHERE ModelID = {ModelID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/models/{ModelID}") 
async def update_models(ModelID, ManufacturerID: int, Name: str, Year: int, IsActive: int):
	'''
	Edit models 
	Argument: 
		ManufacturerID: int
		Name: str
		Year: int
		IsActive: int
	'''

	try:
		models_exists_query = 'SELECT * FROM models WHERE ModelID = %s'
		models_exists_params = (ModelID)
		models_exists_result = execute_query(models_exists_query, models_exists_params)

		if models_exists_result == False:
			raise HTTPException(status_code=404, defail=f"models with ID ModelID not found")

		if models_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE models
		SET ManufacturerID = %s, Name = %s, Year = %s, IsActive = %s
		WHERE ModelID = %s
		'''

		update_params = (ManufacturerID, Name, Year, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"models with ID ModelID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/models/{ModelID}") 
async def delete_models(ModelID: int):
	'''
	Deactivate models 
	Argument: 
		ModelID: int: Model id.
	'''

	try:
		models_exists_query = 'SELECT IsActive FROM models WHERE ModelID = %s'
		models_exists_params = (ModelID,)
		models_exists_result = execute_query(models_exists_query, models_exists_params)

		if not models_exists_result:
			raise HTTPException(status_code=404, detail=f"models with ID ModelID not found")

		if models_exists_result[0]['IsActive'] == 0:
			return {"message": f"models with ID ModelID is already inactive"}

		update_query = 'UPDATE models SET IsActive = 0 WHERE ModelID = %s'
		update_params = (ModelID,)
		execute_query(update_query, update_params)

		return {"message": f"models with ID ModelID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/sales/") 
async def create_sales(sales: sales):
	'''
	Create sales 
	Argument: 
		sales: sales: An object, representing model.
	'''

	try:
		CarID = sales.CarID
		CustomerID = sales.CustomerID
		SaleDate = sales.SaleDate
		SalePrice = sales.SalePrice
		IsActive = sales.IsActive
		query = '''
		INSERT INTO sales (CarID, CustomerID, SaleDate, SalePrice, IsActive)
		VALUES (%s, %s, %s, %s, %s)
		'''

		params = (CarID, CustomerID, SaleDate, SalePrice, IsActive)
		execute_query(query, params)

		return {'message': 'sales successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/{SaleID}") 
async def read_sales(SaleID: int = None):
	'''
	Return sales 
	Argument: 
		SaleID: int: Model id.
	'''

	if not SaleID: 
		query = 'SELECT CarID, CustomerID, SaleDate, SalePrice, IsActive FROM sales'
	else:
		query = f'SELECT CarID, CustomerID, SaleDate, SalePrice, IsActive FROM sales WHERE SaleID = {SaleID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/sales/{SaleID}") 
async def update_sales(SaleID, CarID: int, CustomerID: int, SaleDate: datetime, SalePrice: Decimal, IsActive: int):
	'''
	Edit sales 
	Argument: 
		CarID: int
		CustomerID: int
		SaleDate: datetime
		SalePrice: Decimal
		IsActive: int
	'''

	try:
		sales_exists_query = 'SELECT * FROM sales WHERE SaleID = %s'
		sales_exists_params = (SaleID)
		sales_exists_result = execute_query(sales_exists_query, sales_exists_params)

		if sales_exists_result == False:
			raise HTTPException(status_code=404, defail=f"sales with ID SaleID not found")

		if sales_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE sales
		SET CarID = %s, CustomerID = %s, SaleDate = %s, SalePrice = %s, IsActive = %s
		WHERE SaleID = %s
		'''

		update_params = (CarID, CustomerID, SaleDate, SalePrice, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"sales with ID SaleID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/sales/{SaleID}") 
async def delete_sales(SaleID: int):
	'''
	Deactivate sales 
	Argument: 
		SaleID: int: Model id.
	'''

	try:
		sales_exists_query = 'SELECT IsActive FROM sales WHERE SaleID = %s'
		sales_exists_params = (SaleID,)
		sales_exists_result = execute_query(sales_exists_query, sales_exists_params)

		if not sales_exists_result:
			raise HTTPException(status_code=404, detail=f"sales with ID SaleID not found")

		if sales_exists_result[0]['IsActive'] == 0:
			return {"message": f"sales with ID SaleID is already inactive"}

		update_query = 'UPDATE sales SET IsActive = 0 WHERE SaleID = %s'
		update_params = (SaleID,)
		execute_query(update_query, update_params)

		return {"message": f"sales with ID SaleID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/servicerecords/") 
async def create_servicerecords(servicerecords: servicerecords):
	'''
	Create servicerecords 
	Argument: 
		servicerecords: servicerecords: An object, representing model.
	'''

	try:
		CarID = servicerecords.CarID
		ServiceDate = servicerecords.ServiceDate
		Description = servicerecords.Description
		Cost = servicerecords.Cost
		IsActive = servicerecords.IsActive
		query = '''
		INSERT INTO servicerecords (CarID, ServiceDate, Description, Cost, IsActive)
		VALUES (%s, %s, %s, %s, %s)
		'''

		params = (CarID, ServiceDate, Description, Cost, IsActive)
		execute_query(query, params)

		return {'message': 'servicerecords successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/servicerecords/{ServiceID}") 
async def read_servicerecords(ServiceID: int = None):
	'''
	Return servicerecords 
	Argument: 
		ServiceID: int: Model id.
	'''

	if not ServiceID: 
		query = 'SELECT CarID, ServiceDate, Description, Cost, IsActive FROM servicerecords'
	else:
		query = f'SELECT CarID, ServiceDate, Description, Cost, IsActive FROM servicerecords WHERE ServiceID = {ServiceID}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/servicerecords/{ServiceID}") 
async def update_servicerecords(ServiceID, CarID: int, ServiceDate: datetime, Description: str, Cost: Decimal, IsActive: int):
	'''
	Edit servicerecords 
	Argument: 
		CarID: int
		ServiceDate: datetime
		Description: str
		Cost: Decimal
		IsActive: int
	'''

	try:
		servicerecords_exists_query = 'SELECT * FROM servicerecords WHERE ServiceID = %s'
		servicerecords_exists_params = (ServiceID)
		servicerecords_exists_result = execute_query(servicerecords_exists_query, servicerecords_exists_params)

		if servicerecords_exists_result == False:
			raise HTTPException(status_code=404, defail=f"servicerecords with ID ServiceID not found")

		if servicerecords_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE servicerecords
		SET CarID = %s, ServiceDate = %s, Description = %s, Cost = %s, IsActive = %s
		WHERE ServiceID = %s
		'''

		update_params = (CarID, ServiceDate, Description, Cost, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"servicerecords with ID ServiceID successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/servicerecords/{ServiceID}") 
async def delete_servicerecords(ServiceID: int):
	'''
	Deactivate servicerecords 
	Argument: 
		ServiceID: int: Model id.
	'''

	try:
		servicerecords_exists_query = 'SELECT IsActive FROM servicerecords WHERE ServiceID = %s'
		servicerecords_exists_params = (ServiceID,)
		servicerecords_exists_result = execute_query(servicerecords_exists_query, servicerecords_exists_params)

		if not servicerecords_exists_result:
			raise HTTPException(status_code=404, detail=f"servicerecords with ID ServiceID not found")

		if servicerecords_exists_result[0]['IsActive'] == 0:
			return {"message": f"servicerecords with ID ServiceID is already inactive"}

		update_query = 'UPDATE servicerecords SET IsActive = 0 WHERE ServiceID = %s'
		update_params = (ServiceID,)
		execute_query(update_query, update_params)

		return {"message": f"servicerecords with ID ServiceID successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

