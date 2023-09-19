from flask import Blueprint, abort, render_template
import logging

logger = logging.getLogger("deconz_manager.deconz")

from .connection import deconz

bp = Blueprint("status", __name__, url_prefix="/status")


@bp.route("/lights")
def lights():
    if lights := deconz.get_lights():
        logger.info(f"Lights: {lights}")

        return render_template("status/lights.html")
    else:
        abort(404)
