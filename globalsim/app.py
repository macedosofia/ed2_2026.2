
import os
import secrets
from pathlib import Path
from flask import Flask
from globalsim.routes.countries import blueprint as countries_blueprint
from globalsim.routes.clients import blueprint as clients_blueprint
from globalsim.services.countries import CountryService
from globalsim.services.clients import ClientService
from globalsim.services.packages import PackageService


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        COUNTRIES_PATH=Path(__file__).parent / "data" / "countries.json",
        CLIENTS_PATH=Path(__file__).parent / "data" / "clients.json",
        PACKAGES_PATH=Path(__file__).parent / "data" / "packages.json",
    )
    if config:
        app.config.update(config)

    app.extensions["countries"] = CountryService(app.config["COUNTRIES_PATH"])
    app.extensions["clients"] = ClientService(app.config["CLIENTS_PATH"])
    app.extensions["packages"] = PackageService(app.config["PACKAGES_PATH"])

    app.register_blueprint(countries_blueprint)
    app.register_blueprint(clients_blueprint)

    return app


if __name__ == "__main__":
    create_app().run()
