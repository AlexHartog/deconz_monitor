import logging

from flask import Blueprint, render_template

from deconz_manager.connection import deconz
from deconz_manager.connection import lights as db_lights

logger = logging.getLogger("deconz_manager.app")


bp = Blueprint("app", __name__)


@bp.route("/")
def index():
    return render_template("home.html")
