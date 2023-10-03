import logging

from flask import Blueprint, render_template

logger = logging.getLogger("deconz_manager.app")

bp = Blueprint("app", __name__)


@bp.route("/")
def index():
    return render_template("home.html")
