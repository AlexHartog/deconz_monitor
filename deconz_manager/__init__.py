import logging
import os
import sys
import atexit

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from .lights import lights
from .app import bp as app_bp


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "deconz_manager.sqlite"),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s.%(msecs)d][%(module)s][%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ),
    )
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.logger.info("Reading test config from instance config")
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.logger.info("Creating instance config from test config")

        app.config.from_mapping(test_config)

    app.logger.warning("This is the real logger")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .connection import deconz

    # TODO: add scheduler back in
    scheduler = BackgroundScheduler()
    scheduler.add_job(deconz.update_all_data, trigger="interval", minutes=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    for job in scheduler.get_jobs():
        app.logger.info(f"Running {job.func} at {job.trigger}")

    # Check if we have an API key and otherwise request it

    app.register_blueprint(lights.bp)
    app.register_blueprint(app_bp)
    app.logger.info("Starting app")

    return app
