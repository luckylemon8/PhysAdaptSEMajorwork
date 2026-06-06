from flask import render_template, Blueprint, g, redirect, url_for, request
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

    print(g.user["id"])

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO quiz (user_id) VALUES (?)",
        (g.user["id"],),
    )

    quiz_id = cursor.lastrowid
    question_number = 0

    ids = list(quiz.keys())
    random.shuffle(ids)

    for id in ids:
        question = quiz[id]
        question_id = question["id"]
        question_number += 1
        db.execute(
            "INSERT INTO question_response (quiz_id, question_id, question_number) VALUES (?, ?, ?)",
            (quiz_id, question_id, question_number),
        )
        print(id, question["question_title"])

    db.commit()

    return redirect(
        url_for("question.question_page", question_number=1, quiz_id=quiz_id)
    )


def add_module_questions(questions, quiz, number_of_questions):
    count = 1
    while count <= number_of_questions:
        q = questions[random.randint(0, len(questions) - 1)]
        if q["id"] not in quiz:
            quiz[q["id"]] = q
            count += 1


@bp.route("/question/<int:question_number>/<int:quiz_id>", methods=("GET", "POST"))
def question_page(question_number, quiz_id):

    db = get_db()

    if request.method == "POST":
        answer = request.form["answer"]
        db.execute(
            "UPDATE question_response SET answer = ? WHERE question_number = ? AND quiz_id = ?",
            (answer, question_number, quiz_id),
        )
        question_number += 1

    db.commit()

    question_response = db.execute(
        "SELECT * FROM question_response WHERE question_number = ? AND quiz_id = ?",
        (question_number, quiz_id),
    ).fetchone()

    question = db.execute(
        "SELECT * FROM question WHERE id = ?",
        (question_response["question_id"],),
    ).fetchone()

    print(question)

    return render_template(
        "question/question.html",
        question=question,
        question_response=question_response,
        previous_question_number=(int(question_number) - 1),
        next_question_number=int(question_number) + 1,
    )
