import os
import secrets
from pathlib import Path
from flask import Flask
from routes.countries import blueprint
from services.countries import CountryService


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        COUNTRIES_PATH=Path(__file__).parent / "data" / "countries.json",
    )
    if config:
        app.config.update(config)
    app.extensions["countries"] = CountryService(app.config["COUNTRIES_PATH"])
    app.register_blueprint(blueprint)
    return app


if __name__ == "__main__":
    create_app().run()
