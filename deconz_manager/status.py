from flask import Blueprint, abort, render_template
import logging

logger = logging.getLogger("deconz_manager.deconz")

from .connection import deconz, lights as db_lights

bp = Blueprint("status", __name__, url_prefix="/status")


@bp.route("/lights")
def lights():
    deconz.get_all_data()
    lights = db_lights.get_lights()

    url = deconz.get_connection_url()

    return render_template("status/lights.html", lights=lights, url=url)


@bp.route("/history")
def lights_history():
    lights_history_count = db_lights.get_history_count()

    return render_template(
        "status/lights_history.html", lights_history_count=lights_history_count
    )
