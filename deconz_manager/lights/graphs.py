from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import HoverTool
import logging
from datetime import datetime, timedelta

from deconz_manager.connection import lights as db_lights

logger = logging.getLogger("deconz_manager.lights.graphs")


def create_history_graphs():
    graphs = {}
    grid = gridplot(
        [create_light_history_graph(), create_day_averages()],
        ncols=1,
        sizing_mode="scale_width",
    )
    div, script = components(grid)
    graphs["history"] = {"div": div, "script": script}
    return graphs


def create_light_history_graph():
    history_count = db_lights.get_history_count()
    x = [row["at_time"] for row in history_count]
    y = [row["on_count"] for row in history_count]

    p = figure(
        title="Number of lights on",
        x_axis_label="Date Time",
        y_axis_label="On Count",
        x_axis_type="datetime",
    )

    p.vbar(x=x, top=y, bottom=0, color="#f5da42")
    return p


def create_day_averages():
    day_averages = db_lights.get_day_averages()
    x = [datetime.combine(row["date"], datetime.min.time()) for row in day_averages]
    y = [row["avg_light_on"] for row in day_averages]

    logger.info(f"X: {x}")
    logger.info(f"Y: {y}")

    p = figure(
        title="Average number of lights on",
        x_axis_label="Date",
        y_axis_label="Average",
        x_axis_type="datetime",
    )

    tooltips = [("Date", "@x{%F}"), ("Value", "@top")]
    hover_tool = HoverTool(tooltips=tooltips, formatters={"@x": "datetime"})
    p.add_tools(hover_tool)

    p.vbar(x=x, top=y, bottom=0, color="#f5da42", width=timedelta(days=1) * 0.8)

    return p
