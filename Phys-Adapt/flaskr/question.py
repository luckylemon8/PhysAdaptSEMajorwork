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


@bp.route("/finish_quiz/<int:quiz_id>")
def finish_quiz(quiz_id):
    db = get_db()
    results = db.execute(
        "SELECT question_number, module, question_response.answer as user_answer, question.answer as correct_answer "
        "FROM question_response, question WHERE question_response.question_id = question.id AND quiz_id = ?",
        (quiz_id,),
    ).fetchall()
    for result in results:
        print(result)
        for key in result.keys():
            print("key:" + str(key) + ",value:" + str(result[key]))
    return render_template(
        "question/results-table.html", results=results, quiz_id=quiz_id
    )


@bp.route("/question/<int:question_number>/<int:quiz_id>", methods=("GET", "POST"))
def question_page(question_number, quiz_id):
    db = get_db()

    if request.method == "POST":
        if request.form.get("answer"):
            answer = request.form["answer"]
            db.execute(
                "UPDATE question_response SET answer = ? WHERE question_number = ? AND quiz_id = ?",
                (answer, question_number, quiz_id),
            )

        db.commit()
        if request.form.get("Next"):
            question_number += 1
        elif request.form.get("Previous"):
            question_number -= 1
        elif request.form.get("Finish"):
            update_error_scores(quiz_id)
            db.execute(
                "UPDATE user SET test_your_level_complete = ? WHERE id = ?",
                (1, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("question.finish_quiz", quiz_id=quiz_id))

    question_response = db.execute(
        "SELECT * FROM question_response WHERE question_number = ? AND quiz_id = ?",
        (question_number, quiz_id),
    ).fetchone()

    question = db.execute(
        "SELECT * FROM question WHERE id = ?",
        (question_response["question_id"],),
    ).fetchone()

    previous_question_number = question_number - 1
    next_question_number = question_number + 1
    if next_question_number > 12:
        next_question_number = 0

    print(previous_question_number)
    print(next_question_number)

    return render_template(
        "question/question.html",
        question=question,
        question_response=question_response,
        previous_question_number=previous_question_number,
        next_question_number=next_question_number,
    )


@bp.route("/question_viewer/<int:question_number>/<int:quiz_id>")
def view_question(question_number, quiz_id):
    db = get_db()

    question_response = db.execute(
        "SELECT * FROM question_response WHERE question_number = ? AND quiz_id = ?",
        (question_number, quiz_id),
    ).fetchone()

    question = db.execute(
        "SELECT * FROM question WHERE id = ?",
        (question_response["question_id"],),
    ).fetchone()

    return render_template(
        "question/question_viewer.html",
        question=question,
        question_response=question_response,
    )


def update_error_scores(quiz_id):
    db = get_db()
    base_user_scores = db.execute(
        "SELECT mod_5_error_score, mod_6_error_score, mod_7_error_score, mod_8_error_score FROM error_scores WHERE user_id=?",
        (g.user["id"],),
    ).fetchone()

    results = db.execute(
        "SELECT question_number, module, question_response.answer as user_answer, question.answer as correct_answer "
        "FROM question_response, question WHERE question_response.question_id = question.id AND quiz_id = ?",
        (quiz_id,),
    ).fetchall()

    module_scores = {}

    module_scores[5] = base_user_scores["mod_5_error_score"]
    module_scores[6] = base_user_scores["mod_6_error_score"]
    module_scores[7] = base_user_scores["mod_7_error_score"]
    module_scores[8] = base_user_scores["mod_8_error_score"]

    for result in results:
        if result["user_answer"] != result["correct_answer"]:
            module_scores[result["module"]] += 4
        else:
            module_scores[result["module"]] -= 3

    for key in module_scores.keys():
        if module_scores[key] > 50:
            module_scores[key] = 50
        if module_scores[key] < 0:
            module_scores[key] = 0

    db.execute(
        "UPDATE error_scores SET mod_5_error_score = ?, mod_6_error_score = ?, mod_7_error_score = ?, mod_8_error_score = ? WHERE user_id = ?",
        (
            module_scores[5],
            module_scores[6],
            module_scores[7],
            module_scores[8],
            g.user["id"],
        ),
    )
    db.commit()
