from flask import Blueprint, render_template, abort

import logging

from deconz_manager.connection import deconz, lights as db_lights

logger = logging.getLogger("deconz_manager.lights")


bp = Blueprint("lights", __name__, url_prefix="/lights", template_folder="templates")


@bp.route("/")
def lights():
    deconz.get_all_data()
    lights = db_lights.get_lights()

    url = deconz.get_connection_url()

    return render_template("lights/lights.html", lights=lights, url=url)


@bp.route("/history")
def history():
    lights_history_count = db_lights.get_history_count()

    return render_template(
        "lights/history_table.html", lights_history_count=lights_history_count
    )


@bp.route("/snapshot/<at_time>")
def snapshot(at_time):
    snapshot_data = db_lights.get_snapshot(at_time)

    logger.debug(f"Snapshot data: {snapshot_data}")

    return render_template("lights/history_table.html", snapshot_data=snapshot_data)


@bp.route("create_snapshot")
def create_snapshot():
    db_lights.add_snapshots()
    return "OK"


@bp.route("/history_detail/<id>")
def history_detail(id):
    history_details = db_lights.get_light_history_details(id)

    if len(history_details) == 1:
        details = history_details[0]
    else:
        details = None

    return render_template("lights/history_detail.html", history_details=details)


@bp.route("/history_table")
def history_table():
    lights_history_count = db_lights.get_history_count()

    return render_template(
        "lights/history_table.html", lights_history_count=lights_history_count
    )
