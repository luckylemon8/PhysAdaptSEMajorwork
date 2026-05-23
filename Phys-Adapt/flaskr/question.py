from flask import render_template, Blueprint
from flaskr.db import get_db

bp = Blueprint("question", __name__)


@bp.route("/question")
def question_page():

    db = get_db()

    question = db.execute("SELECT * FROM question ORDER BY RANDOM() LIMIT 1").fetchone()

    print(question)

    return render_template("question/question.html", question=question)
