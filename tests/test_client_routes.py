
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

        self.second_package = {
            "codigo": 301,
            "nome": "Global",
            "dados_gb": 20,
            "validade_dias": 30,
            "paises": ["PT", "ES", "FR", "IT", "BR"],
        }

        self.packages_path.write_text(
            json.dumps([self.package, self.second_package]),
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

        self.assertEqual(
            service.list_all(),
            [self.package, self.second_package],
        )
        self.assertEqual(service.find(102), self.package)
        self.assertEqual(service.find(301), self.second_package)

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


    def sample_form(self):
        return {
            "id": "58372",
            "nome": "Maria Silva",
            "email": "maria@email.com",
            "esim": "ESIM-83921",
            "pacote": "102",
            "status": "ativo",
        }

    def test_create_form_displays_packages(self):
        response = self.client.get("/clients/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cadastrar cliente", response.text)
        self.assertIn("Europa Plus", response.text)
        self.assertFalse(self.clients_path.exists())

    def test_client_list_contains_create_link(self):
        response = self.client.get("/clients")

        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/clients/new"', response.text)

    def test_create_client_persists_record(self):
        response = self.client.post(
            "/clients/new",
            data=self.sample_form(),
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["Location"],
            "/clients/58372",
        )

        service = self.app.extensions["clients"]
        record = service.find(58372)

        self.assertEqual(record["nome"], "Maria Silva")
        self.assertEqual(record["email"], "maria@email.com")
        self.assertEqual(record["esim"], "ESIM-83921")
        self.assertEqual(record["pacote"], 102)
        self.assertEqual(record["status"], "ativo")
        self.assertEqual(service.statistics()["size"], 1)

        self.assertTrue(self.clients_path.exists())

        restarted = create_app(self.app.config)

        self.assertEqual(
            restarted.extensions["clients"].find(58372),
            record,
        )

    def test_create_client_without_optional_fields(self):
        data = self.sample_form()
        data["esim"] = ""
        data["pacote"] = ""

        response = self.client.post(
            "/clients/new",
            data=data,
        )

        self.assertEqual(response.status_code, 303)

        record = self.app.extensions["clients"].find(58372)

        self.assertIsNone(record["esim"])
        self.assertIsNone(record["pacote"])

    def test_create_rejects_duplicate_id(self):
        data = self.sample_form()

        first = self.client.post("/clients/new", data=data)

        self.assertEqual(first.status_code, 303)

        original = self.clients_path.read_bytes()

        second = self.client.post("/clients/new", data=data)

        self.assertEqual(second.status_code, 400)
        self.assertEqual(
            self.app.extensions["clients"].statistics()["size"],
            1,
        )
        self.assertEqual(
            self.clients_path.read_bytes(),
            original,
        )

    def test_create_rejects_invalid_fields(self):
        invalid_fields = [
            ("id", ""),
            ("id", "0"),
            ("id", "-1"),
            ("id", "abc"),
            ("id", "1.5"),
            ("nome", ""),
            ("email", "email-invalido"),
            ("status", ""),
            ("pacote", "abc"),
            ("pacote", "0"),
            ("pacote", "-1"),
            ("pacote", "9999"),
        ]

        for field, value in invalid_fields:
            with self.subTest(field=field, value=value):
                data = self.sample_form()
                data[field] = value

                response = self.client.post(
                    "/clients/new",
                    data=data,
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    self.app.extensions["clients"].list_all(),
                    [],
                )
                self.assertFalse(self.clients_path.exists())

    def test_create_preserves_form_on_error(self):
        data = self.sample_form()
        data["email"] = "email-invalido"

        response = self.client.post(
            "/clients/new",
            data=data,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Maria Silva", response.text)
        self.assertIn("email-invalido", response.text)
        self.assertIn("ESIM-83921", response.text)

    def test_create_handles_persistence_failure(self):
        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            response = self.client.post(
                "/clients/new",
                data=self.sample_form(),
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            self.app.extensions["clients"].list_all(),
            [],
        )
        self.assertFalse(self.clients_path.exists())

    def test_edit_links_are_displayed(self):
        self.create_sample_client()

        listing = self.client.get("/clients")
        detail = self.client.get("/clients/58372")

        self.assertIn(
            'href="/clients/58372/edit"',
            listing.text,
        )
        self.assertIn(
            'href="/clients/58372/edit"',
            detail.text,
        )

    def test_edit_form_displays_existing_client(self):
        self.create_sample_client()

        response = self.client.get("/clients/58372/edit")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Editar cliente", response.text)
        self.assertIn("Maria Silva", response.text)
        self.assertIn("maria@email.com", response.text)
        self.assertIn("ESIM-83921", response.text)
        self.assertIn("readonly", response.text)

    def test_edit_client_persists_changes(self):
        self.create_sample_client()

        data = self.sample_form()
        data.update({
            "nome": "Maria Souza",
            "email": "maria.souza@email.com",
            "esim": "ESIM-99999",
            "status": "inativo",
        })

        response = self.client.post(
            "/clients/58372/edit",
            data=data,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["Location"],
            "/clients/58372",
        )

        service = self.app.extensions["clients"]
        record = service.find(58372)

        self.assertEqual(record["id"], 58372)
        self.assertEqual(record["nome"], "Maria Souza")
        self.assertEqual(record["email"], data["email"])
        self.assertEqual(record["esim"], "ESIM-99999")
        self.assertEqual(record["status"], "inativo")
        self.assertEqual(service.statistics()["size"], 1)

        restarted = create_app(self.app.config)

        self.assertEqual(
            restarted.extensions["clients"].find(58372),
            record,
        )

    def test_edit_rejects_id_change(self):
        record = self.create_sample_client()
        original = self.clients_path.read_bytes()

        data = self.sample_form()
        data["id"] = "99999"

        response = self.client.post(
            "/clients/58372/edit",
            data=data,
        )

        service = self.app.extensions["clients"]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(service.find(58372), record)
        self.assertIsNone(service.find(99999))
        self.assertEqual(
            self.clients_path.read_bytes(),
            original,
        )

    def test_edit_missing_client(self):
        response = self.client.get("/clients/99999/edit")

        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            "/clients/99999/edit",
            data=self.sample_form(),
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_rejects_invalid_fields(self):
        record = self.create_sample_client()
        original = self.clients_path.read_bytes()

        for field, value in [
            ("email", "email-invalido"),
            ("pacote", "9999"),
            ("nome", ""),
            ("status", ""),
        ]:
            with self.subTest(field=field):
                data = self.sample_form()
                data[field] = value

                response = self.client.post(
                    "/clients/58372/edit",
                    data=data,
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    self.app.extensions["clients"].find(58372),
                    record,
                )
                self.assertEqual(
                    self.clients_path.read_bytes(),
                    original,
                )

    def test_edit_removes_optional_associations(self):
        self.create_sample_client()

        data = self.sample_form()
        data["esim"] = ""
        data["pacote"] = ""

        response = self.client.post(
            "/clients/58372/edit",
            data=data,
        )

        self.assertEqual(response.status_code, 303)

        record = self.app.extensions["clients"].find(58372)

        self.assertIsNone(record["esim"])
        self.assertIsNone(record["pacote"])

    def test_edit_handles_persistence_failure(self):
        record = self.create_sample_client()
        original = self.clients_path.read_bytes()

        data = self.sample_form()
        data["nome"] = "Maria Souza"

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            response = self.client.post(
                "/clients/58372/edit",
                data=data,
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            self.app.extensions["clients"].find(58372),
            record,
        )
        self.assertEqual(
            self.clients_path.read_bytes(),
            original,
        )
    def test_edit_changes_package(self):
        self.create_sample_client()

        data = self.sample_form()
        data["pacote"] = "301"

        response = self.client.post(
            "/clients/58372/edit",
            data=data,
        )

        self.assertEqual(response.status_code, 303)

        service = self.app.extensions["clients"]
        record = service.find(58372)

        self.assertEqual(record["pacote"], 301)
        self.assertEqual(record["id"], 58372)
        self.assertEqual(service.statistics()["size"], 1)

        restarted = create_app(self.app.config)

        self.assertEqual(
            restarted.extensions["clients"].find(58372),
            record,
        )

if __name__ == "__main__":
    unittest.main()
