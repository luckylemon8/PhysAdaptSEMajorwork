from flask import render_template, Blueprint
from flaskr.db import get_db

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
    mod_5_questions = db.execute(
        "SELECT * FROM questions WHERE module = '5'"
    ).fetchall()
    mod_6_questions = db.execute(
        "SELECT * FROM questions WHERE module = '6'"
    ).fetchall()
    mod_7_questions = db.execute(
        "SELECT * FROM questions WHERE module = '7'"
    ).fetchall()
    mod_8_questions = db.execute(
        "SELECT * FROM questions WHERE module = '8'"
    ).fetchall()
    return render_template("question/test_your_level.html")


@bp.route("/question")
def question_page():

    db = get_db()

    question = db.execute("SELECT * FROM question ORDER BY RANDOM() LIMIT 1").fetchone()

    print(question)

    return render_template("question/question.html", question=question)
