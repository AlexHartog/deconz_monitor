import logging

from flask import Blueprint, render_template

from deconz_manager.connection import deconz
from deconz_manager.connection import lights as db_lights
from deconz_manager.connection.connection_manager import postgres_db

from . import graphs as light_graphs

logger = logging.getLogger("deconz_manager.lights")


bp = Blueprint(
    "lights",
    __name__,
    url_prefix="/lights",
    template_folder="templates",
)


@bp.route("/")
def lights():
    """Show the current state for all lights."""
    deconz.get_all_data(postgres_db)
    lights = db_lights.get_lights(postgres_db)

    url = deconz.get_connection_url(postgres_db)

    return render_template(
        "lights/lights.html",
        lights=lights,
        url=url,
    )


@bp.route("/snapshot/<snapshot_id>")
def snapshot(snapshot_id):
    """Show details for a specific snapshot."""
    snapshot_lights = sorted(
        db_lights.get_snapshot(postgres_db, snapshot_id),
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

    return render_template(
        "lights/snapshot.html",
        snapshot_lights=snapshot_lights,
        snapshot_data=snapshot_data,
    )


@bp.route("/history_detail/<id>")
def history_detail(id):
    """Show details for a specific history record."""
    history_details = db_lights.get_history_details(postgres_db, id)

    if len(history_details) == 1:
        details = history_details[0]
    else:
        details = None

    return render_template(
        "lights/history_detail.html",
        history_details=details,
    )


@bp.route("/history_table")
def history_table():
    """Get a table of all history. By default show the last 1000 entries."""
    lights_history_count = db_lights.get_history_count(postgres_db, limit=1000)

    return render_template(
        "lights/history_table.html",
        lights_history_count=lights_history_count,
    )


@bp.route("/graphs")
def graphs():
    """Create graphs to display."""
    graphs = light_graphs.create_history_graphs()

    return render_template(
        "lights/graphs.html",
        graphs=graphs,
    )
