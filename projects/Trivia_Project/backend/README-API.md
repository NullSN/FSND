## API Endpoints
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. As well as a string for error messages.

```curl
curl http://localhost:3000/categories
```

```json
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "formatted_list": "1:Science, 2:Art, 3:Geography, 4:History, 5:Entertainment, 6:Sports, ", 
  "success": true
```

GET '/questions'
- Fetches all questions
- Request Arguments: None
- Returns: A jsonify object containing: total paginated questions, number of questions, and a dictionary of categories. Each question contains an answer, category, difficulty, id, and question text.

```curl
curl http://localhost:3000/questions
```
```json
"questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }
], 
  "success": true, 
  "total_questions": 21
```

DELETE '/questions/<int:question_id>
- Deletes question 
- Request Arguments: question_id 
- Returns: A jsonify object containing what question_id was deleted, a success message, and the now total number of questions

```
curl -X DELETE http://localhost:3000/questions/14
```
```json
{
  "deleted": 14, 
  "success": true, 
  "total_questions": 20
}
```

POST '/questions'
- Creates a new question. 
- Request Arguments: answer, category, difficulty, and question.
- Returns the argument along with a success message.

```curl
curl -X POST -H 'Content-Type: application/json' -d '{"question":"How many dog breeds are there?", "answer":"197", "difficulty":5, "category":1}' http://localhost:3000/questions
```
```json
{
  "answer": "197", 
  "category": 1, 
  "difficulty": 5, 
  "question": "How many dog breeds are there?", 
  "success": true
}
```

POST '/search'
- Searches questions based on search term.
- Request Arguments: searchTerm
- Returns all questions that match the search term, the total amount of questions that match the search term, and a success message

```curl
curl -X POST -H 'Content-Type: application/json' -d '{"searchTerm":"dog"}' http://localhost:3000/search
```

```json
{
  "questions": [
    {
      "answer": "197", 
      "category": 1, 
      "difficulty": 5, 
      "id": 26, 
      "question": "How many dog breeds are there?"
    }
  ], 
  "success": true, 
  "totalQuestions": 1
}
```

POST '/categories/questions'
- Fetches all questions from a certain category
- Request Arguments: category_id as an int
- Returns all questions that are in the selected category, the total amount of questions in category, and a success message.

```curl
curl -X POST -H 'Content-Type: application/json' -d '{"category":"4"}' http://localhost:3000/categories/questions
```

```json
{
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Scarab", 
      "category": 4, 
      "difficulty": 4, 
      "id": 23, 
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ], 
  "success": true, 
  "totalQuestions": 3
}
```

POST '/quizzes'
- Returns all questions for the quiz
- Request Arguments: previous questions[list of questions as int], and quiz_category{"type": category, "id":category_id}. If you wish to choose no category, type becomes "click", and id 0.
- Returns all questions for the quiz

```curl
curl -d '{"previous_questions":[],"quiz_category":{"type":"click","id":0}}' -H 'Content-Type:application/json' -X POST http://localhost:5000/quizzes
```

 or 

 ```curl
 curl -d '{"previous_questions":[], "quiz_category":{"type":"Science","id":"1"}}' -H 'Content-Type:application/json' -X POST http://localhost:5000/quizzes
 ```

```json
{
  "previous_questions": [], 
  "question": {
    "answer": "The Liver", 
    "category": 1, 
    "difficulty": 4, 
    "id": 20, 
    "question": "What is the heaviest organ in the human body?"
  }, 
  "quiz": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "197", 
      "category": 1, 
      "difficulty": 5, 
      "id": 26, 
      "question": "How many dog breeds are there?"
    }, 
    {
      "answer": "foobar", 
      "category": 1, 
      "difficulty": 2, 
      "id": 27, 
      "question": "testing order"
    }
  ]
}
```
