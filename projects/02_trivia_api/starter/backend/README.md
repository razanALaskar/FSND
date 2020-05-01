# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## API Documentation
### Endpoints
- [GET /categories](#get-categories)
- [GET /questions](#get-questions)
- [DELETE /questions/<question_id>](#delete-questions)
- [POST /questions](#post-questions)
- [GET /categories/<category_id>/questions](#get-categories-questions)
- [POST /quizzes](#post-quizzes)
- [Example of Errors](#example-errors)

# <a name="get-categories"></a>
#### GET '/categories'
- Fetches a list of all `categories` with its `type` .
- Request Arguments: **None**
- Request Headers : **None**
- Example of Response:
```js
{
  "success": true,
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ]
}
```

# <a name="get-questions"></a>
#### GET '/questions'
- Fetches a list of dictionaries of questions in which the keys are the ids with all available fields, a list of all categories and number of total questions.
- Request Arguments: 
    - **integer** `page` (optional, 10 questions per page, defaults to `1`)
- Request Headers: **None**
- Example of Response:
```js
{
"success": true,
"questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },

 [...]

  ],
  "total_questions": 19,
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
"current_category": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ]

}

```

# <a name="delete-questions"></a>
#### DELETE '/questions/<question_id>'
- Deletes specific question based on given id
- Request Arguments: 
  - **integer** `question_id`
- Request Headers : **None**
- Example of Response:
```js
{
  "success": true,
  "deleted": 10
}
```
# <a name="post-questions"></a>
#### POST '/questions' (search question)
- Searches database for questions with a search term
- Request Arguments: **None**
- Request Headers :
    - **string** `searchTerm` (<span style="color:red">*</span>required)
- Example of Response:`searchTerm : "movie"`
```js
{
  "success": true,
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  
  ],
 
  "total_questions": 19,
  "current_category": [
    {
      "id": 1,
      "type": "Science"
    },
    {
      "id": 2,
      "type": "Art"
    },

   [...] // all current categories

  ]
}

```

#### POST '/questions' (add question)
- Insert a new question into the database.
- Request Arguments: **None**
- Request Headers :
    - **string** `question` (<span style="color:red">*</span>required)
    - **string** `answer` (<span style="color:red">*</span>required)
    - **string** `category` (<span style="color:red">*</span>required)
    - **integer** `difficulty` (<span style="color:red">*</span>required)
- Example of Response:
```js
{
 "success": true,
  "created": 24, 
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
   
   [...] 

  ],
  "total_questions": 20
}

```
# <a name="get-categories-questions"></a>
#### GET '/categories/<category_id>/question'
- Fetches all `questions` (paginated) from one specific category.
- Request Arguments:
  - **integer** `category_id` (<span style="color:red">*</span>required)
  - **integer** `page` (optinal, 10 questions per Page, defaults to `1`)
- Request Headers: **None**
- Example of Response:`category_id : 2`

```js
{
  "success": true,
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Mona Lisa",
      "category": 2,
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    },
    {
      "answer": "One",
      "category": 2,
      "difficulty": 4,
      "id": 18,
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    {
      "answer": "Jackson Pollock",
      "category": 2,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "total_questions": 4,
  "current_category": "2"
}
```
# <a name="post-quizzes"></a>
#### POST '/quizzes'
- Plays quiz game by providing a list of already asked questions and a category to ask for a fitting, random question.
- Request Arguments: **None**
- Request Headers : 
     1. **list** `previous_questions` with **integer** ids from already asked questions
     1. **dict** `quiz_category` (optional) with keys:
        1.  **string** type
        2. **integer** id from category
- Example of Response:

```js
{ 
  "success": true,
  "question": {
    "answer": "The Liver",
    "category": 1,
    "difficulty": 4,
    "id": 20,
    "question": "What is the heaviest organ in the human body?"
  }
}

```
# <a name="example-errors"></a>
#### Example of Errors
- If you try fetch a page which does not have any questions, you will encounter an error which looks like this:

```bash
curl -X GET http://127.0.0.1:5000/questions?page=111111111
```

- Example of Response:

```js
{
  "error": 404,
  "message": "resource not found",
  "success": false
}

```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```