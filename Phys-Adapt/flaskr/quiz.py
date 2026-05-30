from flask import render_template, Blueprint
from flaskr.db import get_db

bp = Blueprint("quiz", __name__)


@bp.route("/welcome")
def welcome():
    return render_template("question/welcome.html")
