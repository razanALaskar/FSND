import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import AuthError, requires_auth
from models import db_drop_and_create_all, setup_db, Actor, Movie, Performance
from config import pagination

ROWS_PER_PAGE = pagination['example']


def create_app(test_config=None):
	'''create and configure the app'''

	app = Flask(__name__)
	setup_db(app)
	# uncomment this if you want to start a new database on app refresh
	# db_drop_and_create_all()

	# ----------------------------------------------------------------------------#
	# CORS (API configuration)
	# ----------------------------------------------------------------------------#

	CORS(app)

	# CORS Headers
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
		return response

	# ----------------------------------------------------------------------------#
	# Custom Functions
	# ----------------------------------------------------------------------------#

	def get_error_message(error, default_text):
		'''Returns default error text or custom error message (if not applicable)
		*Input:
			* <error> system generated error message which contains a description message
			* <string> default text to be used as error message if Error has no specific message
		*Output:
			* <string> specific error message or default text(if no specific message is given)
		'''
		try:
			return error.description['message']
		except:
			return default_text

	def paginate_results(request, selection):
		'''Paginates and formats database queries
		Parameters:
		  * <HTTP object> request, that may contain a "page" value
		  * <database selection> selection of objects, queried from database

		Returns:
		  * <list> list of dictionaries of objects, max. 10 objects
		'''
		# Get page from request. If not given, default to 1
		page = request.args.get('page', 1, type=int)

		start = (page - 1) * ROWS_PER_PAGE
		end = start + ROWS_PER_PAGE

		objects_formatted = [object_name.format() for object_name in selection]
		return objects_formatted[start:end]


	# Endpoint /actors GET/POST/DELETE/PATCH
	@app.route('/actors', methods=['GET'])
	@requires_auth('get:actors')
	def get_actors(payload):
		"""Returns paginated actors object
		Tested by:
		  Success:
			- test_get_all_actors
		  Error:
			- test_error_401_get_all_actors
			- test_error_404_get_actors
		"""
		selection = Actor.query.all()
		actors_paginated = paginate_results(request, selection)

		if len(actors_paginated) == 0:
			abort(404, {'message': 'no actors found in database.'})

		return jsonify({
			'success': True,
			'actors': actors_paginated
		})

	@app.route('/actors', methods=['POST'])
	@requires_auth('post:actors')
	def insert_actors(payload):
		"""Inserts a new Actor
		Tested by:
		  Success:
			- test_create_new_actor
		  Error:
			- test_error_422_new_actor
			- test_error_401_new_actor
		"""
		# Get request json
		body = request.get_json()

		if not body:
			abort(400, {'message': 'request does not contain a valid JSON body.'})

		# Extract name and age value from request body
		name = body.get('name', None)
		age = body.get('age', None)

		# Set gender to value or to 'Other' if not given
		gender = body.get('gender', 'Other')

		# abort if one of these are missing with appropiate error message
		if not name:
			abort(422, {'message': 'no name provided.'})

		if not age:
			abort(422, {'message': 'no age provided.'})

		new_actor = (Actor(
			name=name,
			age=age,
			gender=gender
		))
		new_actor.insert()

		return jsonify({
			'success': True,
			'created': new_actor.id
		})

	@app.route('/actors/<actor_id>', methods=['PATCH'])
	@requires_auth('patch:actors')
	def edit_actors(payload, actor_id):
		"""Edit an existing Actor
		Tested by:
		  Success:
			- test_edit_actor
		  Error:
			- test_error_404_edit_actor
		"""
		# Get request json
		body = request.get_json()

		if not actor_id:
			abort(400, {'message': 'please append an actor id to the request url.'})

		if not body:
			abort(400, {'message': 'request does not contain a valid JSON body.'})

		actor_to_update = Actor.query.filter(Actor.id == actor_id).one_or_none()

		if not actor_to_update:
			abort(404, {'message': 'Actor with id {} not found in database.'.format(actor_id)})


		name = body.get('name', actor_to_update.name)
		age = body.get('age', actor_to_update.age)
		gender = body.get('gender', actor_to_update.gender)

		actor_to_update.name = name
		actor_to_update.age = age
		actor_to_update.gender = gender

		actor_to_update.update()

		return jsonify({
			'success': True,
			'updated': actor_to_update.id,
			'actor': [actor_to_update.format()]
		})

	@app.route('/actors/<actor_id>', methods=['DELETE'])
	@requires_auth('delete:actors')
	def delete_actors(payload, actor_id):
		"""Delete an existing Actor
		Tested by:
		  Success:
			- test_delete_actor
		  Error:
			- test_error_401_delete_actor
			- test_error_404_delete_actor
		"""
		# Abort if no actor_id has been provided
		if not actor_id:
			abort(400, {'message': 'please append an actor id to the request url.'})

		actor_to_delete = Actor.query.filter(Actor.id == actor_id).one_or_none()

		if not actor_to_delete:
			abort(404, {'message': 'Actor with id {} not found in DB.'.format(actor_id)})

		actor_to_delete.delete()

		return jsonify({
			'success': True,
			'deleted': actor_id
		})

	# Endpoint /movies GET/POST/DELETE/PATCH
	@app.route('/movies', methods=['GET'])
	@requires_auth('get:movies')
	def get_movies(payload):
		"""Returns paginated movies object
		Tested by:
		  Success:
			- test_get_all_movies
		  Error:
			- test_error_401_get_all_movies
			- test_error_404_get_movies
		"""
		selection = Movie.query.all()
		movies_paginated = paginate_results(request, selection)

		if len(movies_paginated) == 0:
			abort(404, {'message': 'no movies found in DB.'})

		return jsonify({
			'success': True,
			'movies': movies_paginated
		})

	@app.route('/movies', methods=['POST'])
	@requires_auth('post:movies')
	def insert_movies(payload):
		"""Inserts a new movie
		Tested by:
		  Success:
			- test_create_new_movie
		  Error:
			- test_error_422_new_movie
			- test_error_401_new_movie
		"""
		# Get request json
		body = request.get_json()

		if not body:
			abort(400, {'message': 'request does not contain a valid JSON body.'})

		title = body.get('title', None)
		release_date = body.get('release_date', None)

		if not title:
			abort(422, {'message': 'no title provided.'})

		if not release_date:
			abort(422, {'message': 'no "release_date" provided.'})

		new_movie = (Movie(
			title=title,
			release_date=release_date
		))
		new_movie.insert()

		return jsonify({
			'success': True,
			'created': new_movie.id
		})

	@app.route('/movies/<movie_id>', methods=['PATCH'])
	@requires_auth('patch:movies')
	def edit_movies(payload, movie_id):
		"""Edit an existing Movie
		Tested by:
		  Success:
			- test_edit_movie
		  Error:
			- test_error_404_edit_movie
		"""
		body = request.get_json()

		# Abort if no movie_id or body has been provided
		if not movie_id:
			abort(400, {'message': 'please append an movie id to the request url.'})

		if not body:
			abort(400, {'message': 'request does not contain a valid JSON body.'})

		movie_to_update = Movie.query.filter(Movie.id == movie_id).one_or_none()

		if not movie_to_update:
			abort(404, {'message': 'Movie with id {} not found in DB.'.format(movie_id)})


		title = body.get('title', movie_to_update.title)
		release_date = body.get('release_date', movie_to_update.release_date)

		movie_to_update.title = title
		movie_to_update.release_date = release_date

		movie_to_update.update()

		return jsonify({
			'success': True,
			'edited': movie_to_update.id,
			'movie': [movie_to_update.format()]
		})

	@app.route('/movies/<movie_id>', methods=['DELETE'])
	@requires_auth('delete:movies')
	def delete_movies(payload, movie_id):
		"""Delete an existing Movie
		Tested by:
		  Success:
			- test_delete_movie
		  Error:
			- test_error_401_delete_movie
			- test_error_404_delete_movie
		"""
		# Abort if no movie_id has been provided
		if not movie_id:
			abort(400, {'message': 'please append an movie id to the request url.'})

		movie_to_delete = Movie.query.filter(Movie.id == movie_id).one_or_none()

		if not movie_to_delete:
			abort(404, {'message': 'Movie with id {} not found in DB.'.format(movie_id)})

		movie_to_delete.delete()

		return jsonify({
			'success': True,
			'deleted': movie_id
		})


	# Error Handlers
	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			"success": False,
			"error": 422,
			"message": get_error_message(error, "unprocessable")
		}), 422

	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			"success": False,
			"error": 400,
			"message": get_error_message(error, "bad request")
		}), 400

	@app.errorhandler(404)
	def ressource_not_found(error):
		return jsonify({
			"success": False,
			"error": 404,
			"message": get_error_message(error, "resource not found")
		}), 404

	@app.errorhandler(AuthError)
	def authentification_failed(AuthError):
		return jsonify({
			"success": False,
			"error": AuthError.status_code,
			"message": AuthError.error['description']
		}), AuthError.status_code

	return app


app = create_app()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)