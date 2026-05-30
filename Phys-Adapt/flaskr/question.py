from flask import render_template, Blueprint
from flaskr.db import get_db
import random

bp = Blueprint("question", __name__)


@bp.route("/")
def index():
    return render_template("question/index.html")


@bp.route("/welcome")
def welcome():
    return render_template("question/welcome.html")


@bp.route("/test_your_level")
def test_your_level():
    db = get_db()
    mod_5_questions = db.execute("SELECT * FROM question WHERE module = '5'").fetchall()
    mod_6_questions = db.execute("SELECT * FROM question WHERE module = '6'").fetchall()
    mod_7_questions = db.execute("SELECT * FROM question WHERE module = '7'").fetchall()
    mod_8_questions = db.execute("SELECT * FROM question WHERE module = '8'").fetchall()

    quiz = {}

    add_module_questions(mod_5_questions, quiz, 3)
    add_module_questions(mod_6_questions, quiz, 3)
    add_module_questions(mod_7_questions, quiz, 3)
    add_module_questions(mod_8_questions, quiz, 3)

    print(quiz)

    return render_template("question/test_your_level.html")


def add_module_questions(questions, quiz, number_of_questions):
    count = 1
    while count <= number_of_questions:
        q = questions[random.randint(0, len(questions) - 1)]
        if q["id"] not in quiz:
            quiz[q["id"]] = q
            count += 1


@bp.route("/question")
def question_page():

    db = get_db()

    question = db.execute("SELECT * FROM question ORDER BY RANDOM() LIMIT 1").fetchone()

    print(question)

    return render_template("question/question.html", question=question)
