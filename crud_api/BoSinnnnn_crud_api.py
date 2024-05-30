from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from decimal import Decimal
from BoSinnnnn_pydantic_models import categories, comments, postcategories, posts, tags, users
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

@app.post("/categories/") 
async def create_categories(categories: categories):
	'''
	Create categories 
	Argument: 
		categories: categories: An object, representing model.
	'''

	try:
		name = categories.name
		IsActive = categories.IsActive
		query = '''
		INSERT INTO categories (name, IsActive)
		VALUES (%s, %s)
		'''

		params = (name, IsActive)
		execute_query(query, params)

		return {'message': 'categories successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/{category_id}") 
async def read_categories(category_id: int = None):
	'''
	Return categories 
	Argument: 
		category_id: int: Model id.
	'''

	if not category_id: 
		query = 'SELECT name, IsActive FROM categories'
	else:
		query = f'SELECT name, IsActive FROM categories WHERE category_id = {category_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/categories/{category_id}") 
async def update_categories(category_id, name: str, IsActive: int):
	'''
	Edit categories 
	Argument: 
		name: str
		IsActive: int
	'''

	try:
		categories_exists_query = 'SELECT * FROM categories WHERE category_id = %s'
		categories_exists_params = (category_id)
		categories_exists_result = execute_query(categories_exists_query, categories_exists_params)

		if categories_exists_result == False:
			raise HTTPException(status_code=404, defail=f"categories with ID category_id not found")

		if categories_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE categories
		SET name = %s, IsActive = %s
		WHERE category_id = %s
		'''

		update_params = (name, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"categories with ID category_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/categories/{category_id}") 
async def delete_categories(category_id: int):
	'''
	Deactivate categories 
	Argument: 
		category_id: int: Model id.
	'''

	try:
		categories_exists_query = 'SELECT IsActive FROM categories WHERE category_id = %s'
		categories_exists_params = (category_id,)
		categories_exists_result = execute_query(categories_exists_query, categories_exists_params)

		if not categories_exists_result:
			raise HTTPException(status_code=404, detail=f"categories with ID category_id not found")

		if categories_exists_result[0]['IsActive'] == 0:
			return {"message": f"categories with ID category_id is already inactive"}

		update_query = 'UPDATE categories SET IsActive = 0 WHERE category_id = %s'
		update_params = (category_id,)
		execute_query(update_query, update_params)

		return {"message": f"categories with ID category_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/comments/") 
async def create_comments(comments: comments):
	'''
	Create comments 
	Argument: 
		comments: comments: An object, representing model.
	'''

	try:
		post_id = comments.post_id
		user_id = comments.user_id
		comment = comments.comment
		created_at = comments.created_at
		IsActive = comments.IsActive
		query = '''
		INSERT INTO comments (post_id, user_id, comment, created_at, IsActive)
		VALUES (%s, %s, %s, %s, %s)
		'''

		params = (post_id, user_id, comment, created_at, IsActive)
		execute_query(query, params)

		return {'message': 'comments successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/comments/{comment_id}") 
async def read_comments(comment_id: int = None):
	'''
	Return comments 
	Argument: 
		comment_id: int: Model id.
	'''

	if not comment_id: 
		query = 'SELECT post_id, user_id, comment, created_at, IsActive FROM comments'
	else:
		query = f'SELECT post_id, user_id, comment, created_at, IsActive FROM comments WHERE comment_id = {comment_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/comments/{comment_id}") 
async def update_comments(comment_id, post_id: int, user_id: int, comment: str, created_at: datetime, IsActive: int):
	'''
	Edit comments 
	Argument: 
		post_id: int
		user_id: int
		comment: str
		created_at: datetime
		IsActive: int
	'''

	try:
		comments_exists_query = 'SELECT * FROM comments WHERE comment_id = %s'
		comments_exists_params = (comment_id)
		comments_exists_result = execute_query(comments_exists_query, comments_exists_params)

		if comments_exists_result == False:
			raise HTTPException(status_code=404, defail=f"comments with ID comment_id not found")

		if comments_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE comments
		SET post_id = %s, user_id = %s, comment = %s, created_at = %s, IsActive = %s
		WHERE comment_id = %s
		'''

		update_params = (post_id, user_id, comment, created_at, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"comments with ID comment_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/comments/{comment_id}") 
async def delete_comments(comment_id: int):
	'''
	Deactivate comments 
	Argument: 
		comment_id: int: Model id.
	'''

	try:
		comments_exists_query = 'SELECT IsActive FROM comments WHERE comment_id = %s'
		comments_exists_params = (comment_id,)
		comments_exists_result = execute_query(comments_exists_query, comments_exists_params)

		if not comments_exists_result:
			raise HTTPException(status_code=404, detail=f"comments with ID comment_id not found")

		if comments_exists_result[0]['IsActive'] == 0:
			return {"message": f"comments with ID comment_id is already inactive"}

		update_query = 'UPDATE comments SET IsActive = 0 WHERE comment_id = %s'
		update_params = (comment_id,)
		execute_query(update_query, update_params)

		return {"message": f"comments with ID comment_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/postcategories/") 
async def create_postcategories(postcategories: postcategories):
	'''
	Create postcategories 
	Argument: 
		postcategories: postcategories: An object, representing model.
	'''

	try:
		category_id = postcategories.category_id
		IsActive = postcategories.IsActive
		query = '''
		INSERT INTO postcategories (category_id, IsActive)
		VALUES (%s, %s)
		'''

		params = (category_id, IsActive)
		execute_query(query, params)

		return {'message': 'postcategories successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/postcategories/{post_id}") 
async def read_postcategories(post_id: int = None):
	'''
	Return postcategories 
	Argument: 
		post_id: int: Model id.
	'''

	if not post_id: 
		query = 'SELECT category_id, IsActive FROM postcategories'
	else:
		query = f'SELECT category_id, IsActive FROM postcategories WHERE post_id = {post_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/postcategories/{post_id}") 
async def update_postcategories(post_id, category_id: int, IsActive: int):
	'''
	Edit postcategories 
	Argument: 
		category_id: int
		IsActive: int
	'''

	try:
		postcategories_exists_query = 'SELECT * FROM postcategories WHERE post_id = %s'
		postcategories_exists_params = (post_id)
		postcategories_exists_result = execute_query(postcategories_exists_query, postcategories_exists_params)

		if postcategories_exists_result == False:
			raise HTTPException(status_code=404, defail=f"postcategories with ID post_id not found")

		if postcategories_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE postcategories
		SET category_id = %s, IsActive = %s
		WHERE post_id = %s
		'''

		update_params = (category_id, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"postcategories with ID post_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/postcategories/{post_id}") 
async def delete_postcategories(post_id: int):
	'''
	Deactivate postcategories 
	Argument: 
		post_id: int: Model id.
	'''

	try:
		postcategories_exists_query = 'SELECT IsActive FROM postcategories WHERE post_id = %s'
		postcategories_exists_params = (post_id,)
		postcategories_exists_result = execute_query(postcategories_exists_query, postcategories_exists_params)

		if not postcategories_exists_result:
			raise HTTPException(status_code=404, detail=f"postcategories with ID post_id not found")

		if postcategories_exists_result[0]['IsActive'] == 0:
			return {"message": f"postcategories with ID post_id is already inactive"}

		update_query = 'UPDATE postcategories SET IsActive = 0 WHERE post_id = %s'
		update_params = (post_id,)
		execute_query(update_query, update_params)

		return {"message": f"postcategories with ID post_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/") 
async def create_posts(posts: posts):
	'''
	Create posts 
	Argument: 
		posts: posts: An object, representing model.
	'''

	try:
		user_id = posts.user_id
		title = posts.title
		content = posts.content
		created_at = posts.created_at
		IsActive = posts.IsActive
		query = '''
		INSERT INTO posts (user_id, title, content, created_at, IsActive)
		VALUES (%s, %s, %s, %s, %s)
		'''

		params = (user_id, title, content, created_at, IsActive)
		execute_query(query, params)

		return {'message': 'posts successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/{post_id}") 
async def read_posts(post_id: int = None):
	'''
	Return posts 
	Argument: 
		post_id: int: Model id.
	'''

	if not post_id: 
		query = 'SELECT user_id, title, content, created_at, IsActive FROM posts'
	else:
		query = f'SELECT user_id, title, content, created_at, IsActive FROM posts WHERE post_id = {post_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/posts/{post_id}") 
async def update_posts(post_id, user_id: int, title: str, content: str, created_at: datetime, IsActive: int):
	'''
	Edit posts 
	Argument: 
		user_id: int
		title: str
		content: str
		created_at: datetime
		IsActive: int
	'''

	try:
		posts_exists_query = 'SELECT * FROM posts WHERE post_id = %s'
		posts_exists_params = (post_id)
		posts_exists_result = execute_query(posts_exists_query, posts_exists_params)

		if posts_exists_result == False:
			raise HTTPException(status_code=404, defail=f"posts with ID post_id not found")

		if posts_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE posts
		SET user_id = %s, title = %s, content = %s, created_at = %s, IsActive = %s
		WHERE post_id = %s
		'''

		update_params = (user_id, title, content, created_at, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"posts with ID post_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/posts/{post_id}") 
async def delete_posts(post_id: int):
	'''
	Deactivate posts 
	Argument: 
		post_id: int: Model id.
	'''

	try:
		posts_exists_query = 'SELECT IsActive FROM posts WHERE post_id = %s'
		posts_exists_params = (post_id,)
		posts_exists_result = execute_query(posts_exists_query, posts_exists_params)

		if not posts_exists_result:
			raise HTTPException(status_code=404, detail=f"posts with ID post_id not found")

		if posts_exists_result[0]['IsActive'] == 0:
			return {"message": f"posts with ID post_id is already inactive"}

		update_query = 'UPDATE posts SET IsActive = 0 WHERE post_id = %s'
		update_params = (post_id,)
		execute_query(update_query, update_params)

		return {"message": f"posts with ID post_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/tags/") 
async def create_tags(tags: tags):
	'''
	Create tags 
	Argument: 
		tags: tags: An object, representing model.
	'''

	try:
		post_id = tags.post_id
		tag_name = tags.tag_name
		IsActive = tags.IsActive
		query = '''
		INSERT INTO tags (post_id, tag_name, IsActive)
		VALUES (%s, %s, %s)
		'''

		params = (post_id, tag_name, IsActive)
		execute_query(query, params)

		return {'message': 'tags successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/tags/{tag_id}") 
async def read_tags(tag_id: int = None):
	'''
	Return tags 
	Argument: 
		tag_id: int: Model id.
	'''

	if not tag_id: 
		query = 'SELECT post_id, tag_name, IsActive FROM tags'
	else:
		query = f'SELECT post_id, tag_name, IsActive FROM tags WHERE tag_id = {tag_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/tags/{tag_id}") 
async def update_tags(tag_id, post_id: int, tag_name: str, IsActive: int):
	'''
	Edit tags 
	Argument: 
		post_id: int
		tag_name: str
		IsActive: int
	'''

	try:
		tags_exists_query = 'SELECT * FROM tags WHERE tag_id = %s'
		tags_exists_params = (tag_id)
		tags_exists_result = execute_query(tags_exists_query, tags_exists_params)

		if tags_exists_result == False:
			raise HTTPException(status_code=404, defail=f"tags with ID tag_id not found")

		if tags_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE tags
		SET post_id = %s, tag_name = %s, IsActive = %s
		WHERE tag_id = %s
		'''

		update_params = (post_id, tag_name, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"tags with ID tag_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/tags/{tag_id}") 
async def delete_tags(tag_id: int):
	'''
	Deactivate tags 
	Argument: 
		tag_id: int: Model id.
	'''

	try:
		tags_exists_query = 'SELECT IsActive FROM tags WHERE tag_id = %s'
		tags_exists_params = (tag_id,)
		tags_exists_result = execute_query(tags_exists_query, tags_exists_params)

		if not tags_exists_result:
			raise HTTPException(status_code=404, detail=f"tags with ID tag_id not found")

		if tags_exists_result[0]['IsActive'] == 0:
			return {"message": f"tags with ID tag_id is already inactive"}

		update_query = 'UPDATE tags SET IsActive = 0 WHERE tag_id = %s'
		update_params = (tag_id,)
		execute_query(update_query, update_params)

		return {"message": f"tags with ID tag_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/") 
async def create_users(users: users):
	'''
	Create users 
	Argument: 
		users: users: An object, representing model.
	'''

	try:
		username = users.username
		email = users.email
		password = users.password
		created_at = users.created_at
		IsActive = users.IsActive
		query = '''
		INSERT INTO users (username, email, password, created_at, IsActive)
		VALUES (%s, %s, %s, %s, %s)
		'''

		params = (username, email, password, created_at, IsActive)
		execute_query(query, params)

		return {'message': 'users successfully created'}

	except mysql.connectore.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}") 
async def read_users(user_id: int = None):
	'''
	Return users 
	Argument: 
		user_id: int: Model id.
	'''

	if not user_id: 
		query = 'SELECT username, email, password, created_at, IsActive FROM users'
	else:
		query = f'SELECT username, email, password, created_at, IsActive FROM users WHERE user_id = {user_id}'
	result = execute_query(query)

	#check if deleted
	filtered_result = [record for record in result if record['IsActive']]

	if result:
		return {'data': result}
	else:
		raise HTTPException(status_code=404, detail='Data not found')

@app.put("/users/{user_id}") 
async def update_users(user_id, username: str, email: str, password: str, created_at: datetime, IsActive: int):
	'''
	Edit users 
	Argument: 
		username: str
		email: str
		password: str
		created_at: datetime
		IsActive: int
	'''

	try:
		users_exists_query = 'SELECT * FROM users WHERE user_id = %s'
		users_exists_params = (user_id)
		users_exists_result = execute_query(users_exists_query, users_exists_params)

		if users_exists_result == False:
			raise HTTPException(status_code=404, defail=f"users with ID user_id not found")

		if users_exists_result[0]['IsActive'] == 0:
			raise HTTPException(status_code=403, detail="Cannot update inactive records")

		update_query = '''
		IPDATE users
		SET username = %s, email = %s, password = %s, created_at = %s, IsActive = %s
		WHERE user_id = %s
		'''

		update_params = (username, email, password, created_at, IsActive)
		execute_query(update_query, update_params)

		return {"message": f"users with ID user_id successfully updated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, dateil=str(e))

@app.delete("/users/{user_id}") 
async def delete_users(user_id: int):
	'''
	Deactivate users 
	Argument: 
		user_id: int: Model id.
	'''

	try:
		users_exists_query = 'SELECT IsActive FROM users WHERE user_id = %s'
		users_exists_params = (user_id,)
		users_exists_result = execute_query(users_exists_query, users_exists_params)

		if not users_exists_result:
			raise HTTPException(status_code=404, detail=f"users with ID user_id not found")

		if users_exists_result[0]['IsActive'] == 0:
			return {"message": f"users with ID user_id is already inactive"}

		update_query = 'UPDATE users SET IsActive = 0 WHERE user_id = %s'
		update_params = (user_id,)
		execute_query(update_query, update_params)

		return {"message": f"users with ID user_id successfully deactivated"}
	except mysql.connector.Error as e:
		raise HTTPException(status_code=500, detail=str(e))

