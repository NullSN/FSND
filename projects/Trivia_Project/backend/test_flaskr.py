import os
from unicodedata import category
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import request
from sqlalchemy import desc

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username = os.environ.get('DB_USER')
        self.password = os.environ.get('DBPW')
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.username, self.password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_categories_list(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        question = Question.query.first()
        res = self.client().delete('/questions/' + str(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
        self.assertTrue(data['total_questions'])

    def test_delete_question_doesnt_exist(self):
        res = self.client().delete('/questions/' + str(-1))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_post_question(self):
        question = 'How big was the team behind the hit indie game, Valheim?'
        answer = '5'
        category = 5
        difficulty = 3
        res = self.client().post('/questions', json={'question': question, 'answer': answer,
                                                     'category': category, 'difficulty': difficulty})
        data = json.loads(res.data)
        last_question = Question.query.order_by(desc('id')).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, last_question.question)
        self.assertEqual(answer, last_question.answer)
        self.assertEqual(category, last_question.category)
        self.assertEqual(difficulty, last_question.difficulty)

    def test_post_question_missing_question_or_answer(self):
        question = ''
        answer = '5'
        category = 5
        difficulty = 3
        res = self.client().post('/questions', json={'question': question, 'answer': answer,
                                                     'category': category, 'difficulty': difficulty})

        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'], 'You are missing the question or answer body. Please try again.')

    def test_post_question_missing_difficulty(self):
        question = 'How big was the team behind the hit indie game, Valheim?'
        answer = '5'
        category = 5
        res = self.client().post('/questions', json={'question': question, 'answer': answer,
                                                     'category': category})

        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'], 'Difficulty must be a whole number between 1 and 5.')

    def test_post_question_missing_category(self):
        category_res = self.client().get('/categories')
        category_data = json.loads(category_res.data)
        formatted_list = category_data['formatted_list']
        total_categories = len(category_data['categories'])
        message = (f"The category must be a whole number between 1 and {total_categories}."
                   f"The current list of categories are :{formatted_list}")

        question = 'How big was the team behind the hit indie game, Valheim?'
        answer = '5'
        difficulty = 3
        res = self.client().post('/questions', json={'question': question, 'answer': answer,
                                                     'difficulty': difficulty})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertIn(data['message'], message)

    def test_question_by_category(self):
        category = "1"
        res = self.client().post(
            '/categories/questions', json={'category': category}
        )
        data = json.loads(res.data)

        self.assertEqual(data['category'], category)

    def test_search(self):
        search_term = 'Valheim'
        res = self.client().post(
            '/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        for i in data['questions']:
            self.assertIn(search_term, i['question'])

        self.assertEqual(res.status_code, 200)

    '''
    Is there a way outside of selenium, to go through each step of the quiz?
    1)Start quiz
    2)Answer question
    3)Next questions
    '''

    def test_quiz_start(self):
        res = self.client().post(
            '/quizzes', json={'quiz_category': {'type': 'click', 'id': 0}, 'previous_questions': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_quiz_no_category(self):
        res = self.client().post(
            '/quizzes', json={'quiz_category': {'type': 'click', 'id': 7}, 'previous_questions': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(
            data['message'], "This category doesn't exist")

    def test_quiz_unique(self):
        q1 = Question.query.first()
        previous_questions = [q1.id]
        for i in range(5):
            res = self.client().post(
                '/quizzes', json={'quiz_category': {'type': 'click', 'id': 0}, 'previous_questions': previous_questions})
            data = json.loads(res.data)
            new_question_id = data['question']['id']
            previous_questions.append(new_question_id)

        self.assertEqual(len(data['previous_questions']), len(
            set(data['previous_questions'])))

    def test_quiz_gives_one_question(self):
        res = self.client().post(
            '/quizzes', json={'quiz_category': {'type': 'click', 'id': 0}, 'previous_questions': []})
        data = json.loads(res.data)
        number_of_questions = [(data['question'])]

        self.assertEqual(len(number_of_questions), 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
