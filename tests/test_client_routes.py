
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def create_sample_client(self, client_id=58372, name="Maria Silva"):
        record = {
            "id": client_id,
            "nome": name,
            "email": "maria@email.com",
            "esim": "ESIM-83921",
            "pacote": 102,
            "status": "ativo",
        }

        self.app.extensions["clients"].create(record)
        return record

    def test_navigation_contains_clients_link(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/clients"', response.text)

    def test_empty_client_list(self):
        response = self.client.get("/clients")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nenhum cliente cadastrado.", response.text)

    def test_client_list_is_sorted_by_id(self):
        self.create_sample_client(300, "Cliente C")
        self.create_sample_client(100, "Cliente A")
        self.create_sample_client(200, "Cliente B")

        response = self.client.get("/clients")

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            response.text.index("Cliente A"),
            response.text.index("Cliente B"),
        )
        self.assertLess(
            response.text.index("Cliente B"),
            response.text.index("Cliente C"),
        )

    def test_search_existing_client(self):
        self.create_sample_client()

        response = self.client.get("/clients/search?id=58372")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/clients/58372")

        detail = self.client.get(response.headers["Location"])

        self.assertEqual(detail.status_code, 200)
        self.assertIn("Maria Silva", detail.text)

    def test_search_missing_client(self):
        response = self.client.get("/clients/search?id=99999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Cliente não encontrado.", response.text)

    def test_search_rejects_invalid_ids(self):
        for invalid_id in ["", "0", "-1", "abc", "1.5"]:
            with self.subTest(client_id=invalid_id):
                response = self.client.get(
                    "/clients/search",
                    query_string={"id": invalid_id},
                )

                self.assertEqual(response.status_code, 400)

    def test_client_detail_displays_record(self):
        record = self.create_sample_client()

        response = self.client.get("/clients/58372")

        self.assertEqual(response.status_code, 200)

        for value in record.values():
            self.assertIn(str(value), response.text)

    def test_client_detail_missing(self):
        response = self.client.get("/clients/99999")

        self.assertEqual(response.status_code, 404)

    def test_client_detail_invalid_id(self):
        response = self.client.get("/clients/0")

        self.assertEqual(response.status_code, 400)

    def test_queries_use_btree_without_reading_json(self):
        self.create_sample_client()
        service = self.app.extensions["clients"]

        with patch(
            "globalsim.services.clients.clients_json.load",
            side_effect=AssertionError("unexpected file read"),
        ):
            with patch.object(
                service.tree,
                "find",
                wraps=service.tree.find,
            ) as find:
                response = self.client.get(
                    "/clients/search?id=58372"
                )

                self.assertEqual(response.status_code, 302)
                find.assert_called_once_with(58372)

                detail = self.client.get("/clients/58372")

                self.assertEqual(detail.status_code, 200)
                self.assertEqual(find.call_count, 2)

            listing = self.client.get("/clients")

            self.assertEqual(listing.status_code, 200)
            self.assertIn("Maria Silva", listing.text)


if __name__ == "__main__":
    unittest.main()
