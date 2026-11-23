
import json
import tempfile
import unittest
from pathlib import Path

from globalsim.app import create_app
from globalsim.services.clients import ClientService
from globalsim.services.countries import CountryService
from globalsim.services.packages import PackageService


class ClientRoutesTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.countries_path = Path(self.temp_dir.name) / "countries.json"
        self.clients_path = Path(self.temp_dir.name) / "clients.json"
        self.packages_path = Path(self.temp_dir.name) / "packages.json"

        self.package = {
            "codigo": 102,
            "nome": "Europa Plus",
            "dados_gb": 10,
            "validade_dias": 30,
            "paises": ["PT", "ES", "FR", "IT"],
        }

        self.packages_path.write_text(
            json.dumps([self.package]),
            encoding="utf-8",
        )

        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test",
            "COUNTRIES_PATH": self.countries_path,
            "CLIENTS_PATH": self.clients_path,
            "PACKAGES_PATH": self.packages_path,
        })

        self.client = self.app.test_client()

    def test_services_registered(self):
        self.assertIsInstance(
            self.app.extensions["countries"], CountryService
        )
        self.assertIsInstance(
            self.app.extensions["clients"], ClientService
        )
        self.assertIsInstance(
            self.app.extensions["packages"], PackageService
        )

    def test_client_service_starts_empty(self):
        service = self.app.extensions["clients"]

        self.assertEqual(service.list_all(), [])
        self.assertEqual(service.statistics()["size"], 0)

    def test_package_catalog_loaded(self):
        service = self.app.extensions["packages"]

        self.assertEqual(service.list_all(), [self.package])
        self.assertEqual(service.find(102), self.package)

    def test_initialization_does_not_create_clients_file(self):
        self.assertFalse(self.clients_path.exists())


if __name__ == "__main__":
    unittest.main()
