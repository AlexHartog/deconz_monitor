import pytest
from deconz_manager import create_app


@pytest.fixture()
def app():
    # other setup can go here

    app = create_app()
    yield app

    # clean up / reset resources here
