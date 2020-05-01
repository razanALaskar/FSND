import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  def paginate_questions(request, selection):
	  page = request.args.get('page', 1, type=int)

	  start = (page - 1) * QUESTIONS_PER_PAGE
	  end = start + QUESTIONS_PER_PAGE

	  questions = [question.format() for question in selection]
	  current_questions = questions[start:end]

	  return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_categories():
	  categories = Category.query.all()

	  if not categories:
		  abort(404)

	  categories_all = [category.format() for category in categories]
	  categories_returned = []
	  for cat in categories_all:
		  categories_returned.append(cat['type'])

	  return jsonify({
		  'success': True,
		  'categories': categories_returned
	  })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
	  selection = Question.query.order_by(Question.id).all()
	  questions_paginated = paginate_questions(request, selection)
	  if len(questions_paginated) == 0:
		  abort(404)

	  categories = Category.query.all()
	  categories_all = [category.format() for category in categories]

	  categories_returned = []
	  for cat in categories_all:
		  categories_returned.append(cat['type'])
	  return jsonify({
		  'success': True,
		  'questions': questions_paginated,
		  'total_questions': len(selection),
		  'categories': categories_returned,
		  'current_category': categories_returned  # ???
	  })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
	  question = Question.query.filter(Question.id == question_id).one_or_none()
	  if not question:
		  abort(400)
	  try:
		  question.delete()
		  return jsonify({
			  'success': True,
			  'deleted': question_id
		  })
	  except:
		  abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_or_search_questions():
	  body = request.get_json()

	  if not body:
		  abort(400)

	  search_term = body.get('searchTerm', None)

	  if search_term:
		  questions = Question.query.filter(Question.question.contains(search_term)).all()

		  if not questions:
			  abort(404)

		  questions_found = [question.format() for question in questions]
		  selections = Question.query.order_by(Question.id).all()
		  categories = Category.query.all()
		  categories_all = [category.format() for category in categories]

		  return jsonify({
			  'success': True,
			  'questions': questions_found,
			  'total_questions': len(selections),
			  'current_category': categories_all
		  })

	  new_question = body.get('question', None)
	  new_answer = body.get('answer', None)
	  new_category = body.get('category', None)
	  new_difficulty = body.get('difficulty', None)

	  if not new_question:
		  abort(400)

	  if not new_answer:
		  abort(400)

	  if not new_category:
		  abort(400)

	  if not new_difficulty:
		  abort(400)

	  try:
		  question = Question(
			  question=new_question,
			  answer=new_answer,
			  category=new_category,
			  difficulty=new_difficulty
		  )
		  question.insert()
		  selections = Question.query.order_by(Question.id).all()
		  questions_paginated = paginate_questions(request, selections)
		  return jsonify({
			  'success': True,
			  'created': question.id,
			  'questions': questions_paginated,
			  'total_questions': len(selections)
		  })

	  except:
		  abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<string:category_id>/questions', methods=['GET'])
  def get_questions_from_categories(category_id):
	  selection = (Question.query
				   .filter(Question.category == str(category_id))
				   .order_by(Question.id)
				   .all())

	  if not selection:
		  abort(400)

	  questions_paginated = paginate_questions(request, selection)

	  if not questions_paginated:
		  abort(404)

	  return jsonify({
		  'success': True,
		  'questions': questions_paginated,
		  'total_questions': len(selection),
		  'current_category': category_id
	  })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
	  body = request.get_json()

	  if not body:
		  abort(400)

	  previous_questions = body.get('previous_questions', None)
	  current_category = body.get('quiz_category', None)

	  if not previous_questions:
		  if current_category:
			  questions_raw = (Question.query.filter(Question.category == str(current_category['id'])).all())
		  else:
			  questions_raw = (Question.query.all())
	  else:
		  if current_category:
			  questions_raw = (Question.query.filter(Question.category == str(current_category['id'])).filter(Question.id.notin_(previous_questions)).all())
		  else:
			  questions_raw = (Question.query.filter(Question.id.notin_(previous_questions)).all())

	  questions_formatted = [question.format() for question in questions_raw]
	  if (len(questions_formatted) == 0):
		  abort(404)
	  random_question = questions_formatted[random.randint(0, len(questions_formatted))]
	  return jsonify({
		  'success': True,
		  'question': random_question
	  })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message":"bad request"
      }), 400

  @app.errorhandler(404)
  def ressource_not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message":  "resource not found"
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message":"unprocessable"
      }), 422
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
      }), 500

  return app

    