import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def drinks():
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404)
    all_drinks_short =[]
    for drink in all_drinks:
        drink = drink.short()
        all_drinks_short.append(drink)
    return jsonify({
        'success': True,
        'drinks': all_drinks_short
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    all_drinks = Drink.query.order_by(Drink.id).all()
    if len(all_drinks) == 0:
        all_drinks_long=[]
    all_drinks_long= [drink.long() for drink in all_drinks]
    return jsonify({
        'success': True,
        'drinks': all_drinks_long
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = json.dumps(body.get('recipe', None))

    if not title or not recipe:
        abort(422)

    drink = Drink.query.filter(Drink.title == title).one_or_none()

    if drink:
        abort(409)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            "success": True, "drinks": drink.long()
        })
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()

    if not body:
        abort(404)

    drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()

    updated_title = body.get('title', None)
    updated_recipe = body.get('recipe', None)

    if updated_title:
        drink_to_update.title = body['title']

    if updated_recipe:
        drink_to_update.recipe = """{}""".format(body['recipe'])
    try:
        drink_to_update.update()

        return jsonify({
            'success': True,
            'drinks': drink_to_update.long()
        })
    except Exception:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    if not drink_id:
        abort(422)

    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink_to_delete:
        abort(404)

    drink_to_delete.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    })


## Error Handling


'''
Example error handling for unprocessable entity
'''



'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def ressource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def authentification_failed(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message":"authentification fails"
    }), 401

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

