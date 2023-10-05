import atexit
import logging
import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask

from .app import bp as app_bp
from .connection import deconz
from .connection.connection_manager import postgres_db
from .lights import lights

load_dotenv()


def create_app(test_config=None):
    """Create the Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "deconz_manager.sqlite"),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s.%(msecs)d][%(module)s][%(levelname)s]" " %(message)s",
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

    if missing := missing_required_env_variables():
        app.logger.error(
            f"Closing down. Missing required environment variables: "
            f"{', '.join(missing)}"
        )
        exit()

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if os.getenv("ENABLE_SCHEDULER") == "True":
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            deconz.update_all_data, args=[postgres_db], trigger="interval", minutes=1
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

        for job in scheduler.get_jobs():
            app.logger.info(
                f"Running {job.func} with args: {job.args} at {job.trigger}"
            )

    app.register_blueprint(lights.bp)
    app.register_blueprint(app_bp)
    app.logger.info("Starting app")

    return app


def missing_required_env_variables() -> [str]:
    required_variables = ["DB_USER", "DB_HOST", "DB_PASSWORD", "DB_DATABASE"]

    return [variable for variable in required_variables if not os.getenv(variable)]
