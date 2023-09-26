import logging

from flask import Blueprint, abort, render_template

from deconz_manager.connection import deconz
from deconz_manager.connection import lights as db_lights

from . import graphs as light_graphs

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


@bp.route("/snapshot/<snapshot_id>")
def snapshot(snapshot_id):
    snapshot_lights = sorted(
        db_lights.get_snapshot(snapshot_id),
        key=lambda snapshot: (
            -snapshot["state_reachable"],
            -snapshot["state_on"],
            snapshot["light_name"],
        ),
    )

    snapshot_data = {
        "num_on": len(
            [
                light
                for light in snapshot_lights
                if light["state_on"] and light["state_reachable"]
            ]
        ),
        "total_count": len(
            [light for light in snapshot_lights if light["state_reachable"]]
        ),
        "timestamp": snapshot_lights[0]["at_time"],
    }

    logger.debug(f"Snapshot data: {snapshot_lights}")

    return render_template(
        "lights/snapshot.html",
        snapshot_lights=snapshot_lights,
        snapshot_data=snapshot_data,
    )


@bp.route("/history_detail/<id>")
def history_detail(id):
    history_details = db_lights.get_history_details(id)

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


@bp.route("/graphs")
def graphs():
    graphs = light_graphs.create_history_graphs()

    return render_template("lights/graphs.html", graphs=graphs)
