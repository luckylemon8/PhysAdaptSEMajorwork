from flask import render_template, Blueprint, g, redirect, url_for, request
from flaskr.db import get_db, get_user_scores
import random
from flaskr.auth import login_required

bp = Blueprint("question", __name__)


@bp.route("/")
def index():
    return render_template("question/index.html")


@bp.route("/welcome")
@login_required
def welcome():
    score_data = generate_score_data()
    print(score_data)
    return render_template("question/welcome.html", score_data=score_data)


@bp.route("/new_user")
@login_required
def new_user():
    return render_template("question/test_your_level.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    error_scores = db.execute(
        "SELECT * FROM error_scores WHERE user_id = ? ORDER BY updated_date_time DESC LIMIT 8",
        (g.user["id"],),
    ).fetchall()

    error_scores.reverse()
    dashboard_data = []

    score = error_scores[1]
    snapshot = {}

    snapshot["mod_5_score"] = str(2 * (50 - int(score["mod_5_error_score"])))
    snapshot["mod_5_start"] = str(int(snapshot["mod_5_score"]) / 100)
    snapshot["mod_5_end"] = str(int(snapshot["mod_5_score"]) / 100)
    snapshot["mod_6_score"] = str(2 * (50 - int(score["mod_6_error_score"])))
    snapshot["mod_6_start"] = str(int(snapshot["mod_6_score"]) / 100)
    snapshot["mod_6_end"] = str(int(snapshot["mod_6_score"]) / 100)
    snapshot["mod_7_score"] = str(2 * (50 - int(score["mod_7_error_score"])))
    snapshot["mod_7_start"] = str(int(snapshot["mod_7_score"]) / 100)
    snapshot["mod_7_end"] = str(int(snapshot["mod_7_score"]) / 100)
    snapshot["mod_8_score"] = str(2 * (50 - int(score["mod_8_error_score"])))
    snapshot["mod_8_start"] = str(int(snapshot["mod_8_score"]) / 100)
    snapshot["mod_8_end"] = str(int(snapshot["mod_8_score"]) / 100)
    snapshot["date"] = score["updated_date_time"].strftime("%d-%m-%y")

    dashboard_data.append(snapshot)

    previous_mod_5_score = str(2 * (50 - int(score["mod_5_error_score"])))
    previous_mod_6_score = str(2 * (50 - int(score["mod_6_error_score"])))
    previous_mod_7_score = str(2 * (50 - int(score["mod_7_error_score"])))
    previous_mod_8_score = str(2 * (50 - int(score["mod_8_error_score"])))
    for score in error_scores[2:]:
        snapshot = {}

        snapshot["mod_5_score"] = str(2 * (50 - int(score["mod_5_error_score"])))
        snapshot["mod_5_start"] = str(int(previous_mod_5_score) / 100)
        snapshot["mod_5_end"] = str(int(snapshot["mod_5_score"]) / 100)
        previous_mod_5_score = snapshot["mod_5_score"]

        snapshot["mod_6_score"] = str(2 * (50 - int(score["mod_6_error_score"])))
        snapshot["mod_6_start"] = str(int(previous_mod_6_score) / 100)
        snapshot["mod_6_end"] = str(int(snapshot["mod_6_score"]) / 100)
        previous_mod_6_score = snapshot["mod_6_score"]

        snapshot["mod_7_score"] = str(2 * (50 - int(score["mod_7_error_score"])))
        snapshot["mod_7_start"] = str(int(previous_mod_7_score) / 100)
        snapshot["mod_7_end"] = str(int(snapshot["mod_7_score"]) / 100)
        previous_mod_7_score = snapshot["mod_7_score"]

        snapshot["mod_8_score"] = str(2 * (50 - int(score["mod_8_error_score"])))
        snapshot["mod_8_start"] = str(int(previous_mod_8_score) / 100)
        snapshot["mod_8_end"] = str(int(snapshot["mod_8_score"]) / 100)
        previous_mod_8_score = snapshot["mod_8_score"]

        snapshot["date"] = score["updated_date_time"].strftime("%d-%m-%y")
        print(snapshot)
        dashboard_data.append(snapshot)

    return render_template("question/dashboard.html", dashboard_data=dashboard_data)


def generate_score_data():
    db = get_db()

    score_data = []
    user_scores = get_user_scores()

    score_data.append(
        module_score("Advanced Mechanics", user_scores["mod_5_error_score"])
    )
    score_data.append(
        module_score("Electromagnetics", user_scores["mod_6_error_score"])
    )
    score_data.append(
        module_score("The Nature of Light", user_scores["mod_7_error_score"])
    )
    score_data.append(
        module_score("From the Universe to the Atom", user_scores["mod_8_error_score"])
    )

    return score_data


def module_score(module_name, error_score):
    score = {
        "module_name": module_name,
        "incorrect_score": error_score,
        "incorrect_percent": error_score * 2,
        "correct_score": 50 - error_score,
        "correct_percent": 2 * (50 - error_score),
    }
    return score


@bp.route("/test_your_level")
@login_required
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


@bp.route("/adaptive_quiz")
@login_required
def adaptive_quiz():
    db = get_db()
    mod_5_questions = db.execute("SELECT * FROM question WHERE module = '5'").fetchall()
    mod_6_questions = db.execute("SELECT * FROM question WHERE module = '6'").fetchall()
    mod_7_questions = db.execute("SELECT * FROM question WHERE module = '7'").fetchall()
    mod_8_questions = db.execute("SELECT * FROM question WHERE module = '8'").fetchall()

    quiz = {}
    TOTAL_QUESTIONS = 20

    user_scores = get_user_scores()

    total_error_score = int(
        user_scores["mod_5_error_score"]
        + user_scores["mod_6_error_score"]
        + user_scores["mod_7_error_score"]
        + user_scores["mod_8_error_score"]
    )

    print(total_error_score)

    if total_error_score == 0:
        mod_5_question_amount = 5
        mod_6_question_amount = 5
        mod_7_question_amount = 5
        mod_8_question_amount = 5

    else:
        mod_5_question_amount = int(
            user_scores["mod_5_error_score"] / total_error_score * TOTAL_QUESTIONS
        )
        mod_6_question_amount = int(
            user_scores["mod_6_error_score"] / total_error_score * TOTAL_QUESTIONS
        )
        mod_7_question_amount = int(
            user_scores["mod_7_error_score"] / total_error_score * TOTAL_QUESTIONS
        )
        mod_8_question_amount = int(
            TOTAL_QUESTIONS
            - (mod_5_question_amount + mod_6_question_amount + mod_7_question_amount)
        )

        print(
            mod_5_question_amount,
            mod_6_question_amount,
            mod_7_question_amount,
            mod_8_question_amount,
        )

    add_module_questions(mod_5_questions, quiz, mod_5_question_amount)
    add_module_questions(mod_6_questions, quiz, mod_6_question_amount)
    add_module_questions(mod_7_questions, quiz, mod_7_question_amount)
    add_module_questions(mod_8_questions, quiz, mod_8_question_amount)

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
@login_required
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
    correct_amount = sum(
        1 for result in results if result["user_answer"] == result["correct_answer"]
    )
    total_questions = 0
    for r in results:
        total_questions += 1
    percentage = (correct_amount / total_questions) * 100 if total_questions > 0 else 0
    percentage = round(percentage, 1)
    total_questions = str(total_questions)

    return render_template(
        "question/results-table.html",
        results=results,
        quiz_id=quiz_id,
        correct_amount=correct_amount,
        percentage=percentage,
    )


@bp.route("/question/<int:question_number>/<int:quiz_id>", methods=("GET", "POST"))
@login_required
def question_page(question_number, quiz_id):
    db = get_db()

    total_questions = db.execute(
        "SELECT COUNT(*) FROM question_response WHERE quiz_id = ?",
        (quiz_id,),
    ).fetchone()[0]

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
    if next_question_number > total_questions:
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
@login_required
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
    base_user_scores = get_user_scores()

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
        "INSERT INTO error_scores (mod_5_error_score, mod_6_error_score, mod_7_error_score, mod_8_error_score, user_id) VALUES (?, ?, ?, ?, ?)",
        (
            module_scores[5],
            module_scores[6],
            module_scores[7],
            module_scores[8],
            g.user["id"],
        ),
    )
    db.commit()
