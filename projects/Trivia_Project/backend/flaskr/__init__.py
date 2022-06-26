import os
from unicodedata import category
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # https://knowledge.udacity.com/questions/421676
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, PUT, POST, DELETE, OPTIONS")
        return response

    # https://knowledge.udacity.com/questions/116054
    # This function mirrors the method from the chapters leading up to this quiz
    def paginate_questions(request, question_list):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in question_list]
        paginate_questions = questions[start:end]
        return paginate_questions

    def dict_of_categories():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return categories

    def list_of_categories():
        categories = dict_of_categories()
        formatted_categories = ''
        for key, value in categories.items():
            formatted_categories += f'{key}:{value}, '
        return formatted_categories

    # Wanted a way to validate fields
    def empty_check(response):
        if response == '' or response == None:
            return True

    @app.route('/categories', methods=['GET'])
    def get_categories():
        dict_of_categories()
        list_of_categories()
        return jsonify({
            'success': True,
            'categories': dict_of_categories(),
            'formatted_list': list_of_categories()
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions_list = Question.query.all()
        paginated_questions = paginate_questions(request, questions_list)
        if len(paginated_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions_list),
            'categories': dict_of_categories()
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        question.delete()
        questions = Question.query.all()
        return jsonify({
            'success': True,
            'deleted': question.id,
            'total_questions': len(questions)
        })

    @app.route('/questions', methods=['POST'])
    def post_question():
        # I wanted to validate the question, without setting up wtforms like in the last project.
        # Wtforms would have been a cleaner solution, but idk if it was out of scope for this project.
        total_categories = len(dict_of_categories())
        data = request.get_json()

        question = data.get('question')
        answer = data.get('answer')
        if empty_check(question) or empty_check(answer):
            abort(500, 'You are missing the question or answer body. Please try again.')

        difficulty = data.get('difficulty')
        if difficulty not in range(1, 6) or empty_check(difficulty):
            abort(500, 'Difficulty must be a whole number between 1 and 5.')

        category = data.get('category')
        if category not in range(1, total_categories) or empty_check(category):
            abort(
                500, f"The category must be a whole number between 1 and {total_categories}."
                f"The current list of categories are :{list_of_categories()}")

        new_question = Question(question, answer, category, difficulty)
        new_question.insert()

        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'difficulty': difficulty,
            'category': category
        })

    @app.route('/search', methods=['POST'])
    def search_questions():
        data = request.get_json()
        search_term = data.get('searchTerm')
        formatted_search_term = '%{}%'.format(search_term)
        search_results = Question.query.filter(
            Question.question.ilike(formatted_search_term)).all()
        paginate_search = paginate_questions(request, search_results)

        return jsonify({
            'success': True,
            'questions': paginate_search,
            'totalQuestions': len(paginate_search)
        })

    @app.route('/categories/questions', methods=['POST'])
    def questions_by_category():
        data = request.get_json()
        category_id = data.get('category')
        search_results = Question.query.filter(
            Question.category == category_id)
        paginate_search = paginate_questions(request, search_results)
        return jsonify({
            'success': True,
            'questions': paginate_search,
            'totalQuestions': len(paginate_search),
            'category': category_id
        })

    # https://knowledge.udacity.com/questions/365775
    @app.route('/quizzes', methods=['POST'])
    def play_game():
        data = request.get_json()
        quiz_category = data.get('quiz_category', None)
        previous_questions = data.get('previous_questions', [])

        if quiz_category['id'] == 0:
            list_of_questions = Question.query.all()
        else:
            list_of_questions = Question.query.filter(
                Question.category == quiz_category['id']).all()
        if not list_of_questions:
            if quiz_category['id'] not in range(1, 6):
                abort(422, "This category doesn't exist")
            else:
                abort(422, "There are no questions for this category.")

        try:
            quiz = []
            for question in list_of_questions:
                if question.id not in previous_questions:
                    quiz.append(question.format())

            if len(quiz) != 0:
                result = random.choice(quiz)
                return jsonify({'question': result,
                                'previous_questions': previous_questions,
                                'quiz': quiz})
            else:
                return jsonify({'question': False,
                                'quiz': quiz})
        except:
            abort(422, "Unable to procces request")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    # https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha/21297608
    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': error.description
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': error.description
        }), 500

    return app
