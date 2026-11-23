
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

    def create_coverage_country(self, code="IT"):
        countries = {
            "IT": {
                "codigo": "IT",
                "pais": "Italia",
                "regiao": "Europa",
                "operadora": "TIM",
                "tecnologia": "5G",
            },
            "BR": {
                "codigo": "BR",
                "pais": "Brasil",
                "regiao": "America",
                "operadora": "Claro",
                "tecnologia": "5G",
            },
        }

        record = countries[code]

        self.app.extensions["countries"].create(record)

        return record

    def test_coverage_form(self):
        response = self.client.get("/clients/coverage")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="client_id"', response.data)
        self.assertIn(b'name="codigo"', response.data)

    def test_coverage_navigation_links(self):
        self.create_sample_client()

        home = self.client.get("/")
        listing = self.client.get("/clients")
        detail = self.client.get("/clients/58372")

        self.assertEqual(home.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(detail.status_code, 200)

        self.assertIn(b"/clients/coverage", home.data)

        self.assertIn(
            b"Consultar cobertura de clientes",
            listing.data,
        )

        self.assertIn(
            b"/clients/coverage?client_id=58372",
            detail.data,
        )

    def test_coverage_prefills_client_id(self):
        response = self.client.get(
            "/clients/coverage?client_id=58372"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            b'value="58372"',
            response.data,
        )

        self.assertNotIn(
            b'class="message error"',
            response.data,
        )

    def test_coverage_compatible_package(self):
        self.create_sample_client()
        self.create_coverage_country()

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=IT"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Maria Silva", html)
        self.assertIn("ESIM-83921", html)
        self.assertIn("Italia", html)
        self.assertIn("TIM", html)
        self.assertIn("5G", html)
        self.assertIn("Europa Plus", html)

        self.assertIn(
            "O país está incluído no pacote contratado.",
            html,
        )

    def test_coverage_incompatible_package(self):
        self.create_sample_client()
        self.create_coverage_country("BR")

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=BR"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Brasil", html)
        self.assertIn("Europa Plus", html)

        self.assertIn(
            "O país não está incluído no pacote contratado.",
            html,
        )

    def test_coverage_without_optional_associations(self):
        self.create_sample_client()
        self.create_coverage_country()

        self.app.extensions["clients"].update(
            58372,
            {
                "esim": None,
                "pacote": None,
            },
        )

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=IT"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Maria Silva", html)
        self.assertIn("Italia", html)
        self.assertIn("Não associado", html)

        self.assertIn(
            "O cliente não possui pacote associado.",
            html,
        )

    def test_coverage_without_esim(self):
        self.create_sample_client()
        self.create_coverage_country()

        self.app.extensions["clients"].update(
            58372,
            {"esim": None},
        )

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=IT"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Não associado", html)
        self.assertIn("Europa Plus", html)

        self.assertIn(
            "O país está incluído no pacote contratado.",
            html,
        )

    def test_coverage_missing_package_in_catalog(self):
        self.create_sample_client()
        self.create_coverage_country()

        self.app.extensions["clients"].update(
            58372,
            {"pacote": 9999},
        )

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=IT"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Maria Silva", html)
        self.assertIn("Italia", html)

        self.assertIn(
            "O pacote associado não foi encontrado no catálogo.",
            html,
        )

    def test_coverage_normalizes_country_code(self):
        self.create_sample_client()
        self.create_coverage_country()

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=it"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(b"Italia", response.data)
        self.assertIn(b'value="IT"', response.data)

    def test_coverage_missing_client(self):
        self.create_coverage_country()

        response = self.client.get(
            "/clients/coverage?client_id=99999&codigo=IT"
        )

        self.assertEqual(response.status_code, 404)

        html = response.get_data(as_text=True)

        self.assertIn("Cliente não encontrado.", html)
        self.assertIn("Italia", html)

    def test_coverage_missing_country(self):
        self.create_sample_client()

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=ZZ"
        )

        self.assertEqual(response.status_code, 404)

        html = response.get_data(as_text=True)

        self.assertIn("País não cadastrado.", html)
        self.assertIn("Maria Silva", html)

    def test_coverage_rejects_invalid_client_ids(self):
        for client_id in ("", "0", "-1", "abc", "1.5"):
            with self.subTest(client_id=client_id):
                response = self.client.get(
                    "/clients/coverage",
                    query_string={
                        "client_id": client_id,
                        "codigo": "IT",
                    },
                )

                self.assertEqual(response.status_code, 400)

                self.assertIn(
                    "O ID deve ser um inteiro positivo.",
                    response.get_data(as_text=True),
                )

    def test_coverage_rejects_invalid_country_codes(self):
        self.create_sample_client()

        for code in ("", "I", "ITA", "12", "I1"):
            with self.subTest(code=code):
                response = self.client.get(
                    "/clients/coverage",
                    query_string={
                        "client_id": "58372",
                        "codigo": code,
                    },
                )

                self.assertEqual(response.status_code, 400)

    def test_coverage_requires_client_id_on_search(self):
        response = self.client.get(
            "/clients/coverage?codigo=IT"
        )

        self.assertEqual(response.status_code, 400)

    def test_coverage_rejects_post(self):
        response = self.client.post(
            "/clients/coverage"
        )

        self.assertEqual(response.status_code, 405)

    def test_coverage_uses_data_structures_directly(self):
        self.create_sample_client()
        self.create_coverage_country()

        cs = self.app.extensions["clients"]
        hs = self.app.extensions["countries"]

        with patch.object(
            cs.tree,
            "find",
            wraps=cs.tree.find,
        ) as btree_find, patch.object(
            hs.table,
            "find",
            wraps=hs.table.find,
        ) as hash_find:

            response = self.client.get(
                "/clients/coverage?client_id=58372&codigo=IT"
            )

            self.assertEqual(response.status_code, 200)

            btree_find.assert_called_once_with(58372)
            hash_find.assert_called_once_with("IT")

    def test_coverage_does_not_reload_json(self):
        self.create_sample_client()
        self.create_coverage_country()

        targets = (
            "globalsim.services.clients.clients_json.load",
            "globalsim.services.countries.countries_json.load",
            "globalsim.services.packages.packages_json.load",
        )

        for target in targets:
            with self.subTest(target=target):
                with patch(
                    target,
                    side_effect=AssertionError(
                        "JSON recarregado durante consulta"
                    ),
                ) as loader:

                    response = self.client.get(
                        "/clients/coverage?client_id=58372&codigo=IT"
                    )

                    self.assertEqual(response.status_code, 200)

                    loader.assert_not_called()

    def test_coverage_does_not_list_all_records(self):
        self.create_sample_client()
        self.create_coverage_country()

        cs = self.app.extensions["clients"]
        hs = self.app.extensions["countries"]

        with patch.object(
            cs.tree,
            "list_all",
            side_effect=AssertionError(
                "Listagem indevida da Arvore B"
            ),
        ) as btree_list, patch.object(
            hs.table,
            "list_all",
            side_effect=AssertionError(
                "Listagem indevida da Tabela Hash"
            ),
        ) as hash_list:

            response = self.client.get(
                "/clients/coverage?client_id=58372&codigo=IT"
            )

            self.assertEqual(response.status_code, 200)

            btree_list.assert_not_called()
            hash_list.assert_not_called()

    def test_coverage_preserves_records_and_json(self):
        self.create_sample_client()
        self.create_coverage_country()

        cs = self.app.extensions["clients"]
        hs = self.app.extensions["countries"]

        clients_before = self.clients_path.read_bytes()
        countries_before = self.countries_path.read_bytes()
        packages_before = self.packages_path.read_bytes()

        client_records = cs.list_all()
        country_records = hs.list_all()

        response = self.client.get(
            "/clients/coverage?client_id=58372&codigo=IT"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.clients_path.read_bytes(),
            clients_before,
        )

        self.assertEqual(
            self.countries_path.read_bytes(),
            countries_before,
        )

        self.assertEqual(
            self.packages_path.read_bytes(),
            packages_before,
        )

        self.assertEqual(
            cs.list_all(),
            client_records,
        )

        self.assertEqual(
            hs.list_all(),
            country_records,
        )


    def create_instrumentation_clients(self):
        for client_id in range(1, 7):
            self.create_sample_client(
                client_id=client_id,
                name=f"Cliente {client_id}",
            )

    def test_instrumentation_empty_tree(self):
        response = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Instrumentação da Árvore B", html)
        self.assertIn("Clientes cadastrados: 0", html)
        self.assertIn("Altura da árvore: 0", html)
        self.assertIn("Quantidade de nós: 0", html)
        self.assertIn("Divisões de nós: 0", html)
        self.assertIn("Total de buscas: 0", html)

        self.assertIn(
            "Nenhum cliente cadastrado na Árvore B.",
            html,
        )

        self.assertFalse(self.clients_path.exists())

    def test_instrumentation_single_client(self):
        self.create_sample_client()

        response = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Clientes cadastrados: 1", html)
        self.assertIn("Altura da árvore: 1", html)
        self.assertIn("Quantidade de nós: 1", html)
        self.assertIn("Divisões de nós: 0", html)
        self.assertIn("Total de buscas: 0", html)

    def test_instrumentation_after_node_split(self):
        self.create_instrumentation_clients()

        response = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)

        self.assertIn("Clientes cadastrados: 6", html)
        self.assertIn("Altura da árvore: 2", html)
        self.assertIn("Quantidade de nós: 3", html)
        self.assertIn("Divisões de nós: 1", html)

        self.assertNotIn(
            "Nenhum cliente cadastrado na Árvore B.",
            html,
        )

    def test_instrumentation_counts_lookups(self):
        self.create_instrumentation_clients()

        found = self.client.get(
            "/clients/search?id=3"
        )

        missing = self.client.get(
            "/clients/search?id=999"
        )

        detail = self.client.get(
            "/clients/3"
        )

        self.assertEqual(found.status_code, 302)
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(detail.status_code, 200)

        response = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "Total de buscas: 3",
            response.get_data(as_text=True),
        )

    def test_instrumentation_does_not_change_statistics(self):
        self.create_instrumentation_clients()

        service = self.app.extensions["clients"]

        service.find(3)
        service.find(999)

        before = service.statistics()

        for _ in range(3):
            response = self.client.get(
                "/clients/instrumentation"
            )

            self.assertEqual(response.status_code, 200)

        self.assertEqual(
            service.statistics(),
            before,
        )

    def test_instrumentation_navigation_links(self):
        home = self.client.get("/")
        listing = self.client.get("/clients")

        metrics = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(home.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(metrics.status_code, 200)

        self.assertIn(
            b'href="/clients/instrumentation"',
            home.data,
        )

        self.assertIn(
            "Consultar estatísticas da Árvore B",
            listing.get_data(as_text=True),
        )

        self.assertIn(
            "Voltar para a lista de clientes",
            metrics.get_data(as_text=True),
        )

        self.assertIn(
            b'href="/clients"',
            metrics.data,
        )

        self.assertEqual(
            self.client.get("/instrumentation").status_code,
            200,
        )

    def test_instrumentation_rejects_post(self):
        response = self.client.post(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 405)

    def test_instrumentation_uses_btree_statistics(self):
        self.create_instrumentation_clients()

        service = self.app.extensions["clients"]

        with patch.object(
            service.tree,
            "statistics",
            wraps=service.tree.statistics,
        ) as statistics:

            response = self.client.get(
                "/clients/instrumentation"
            )

            self.assertEqual(response.status_code, 200)

            statistics.assert_called_once_with()

    def test_instrumentation_does_not_reload_json(self):
        self.create_instrumentation_clients()

        targets = (
            "globalsim.services.clients.clients_json.load",
            "globalsim.services.countries.countries_json.load",
            "globalsim.services.packages.packages_json.load",
        )

        for target in targets:
            with self.subTest(target=target):
                with patch(
                    target,
                    side_effect=AssertionError(
                        "JSON recarregado indevidamente"
                    ),
                ) as loader:

                    response = self.client.get(
                        "/clients/instrumentation"
                    )

                    self.assertEqual(
                        response.status_code,
                        200,
                    )

                    loader.assert_not_called()

    def test_instrumentation_does_not_list_all_clients(self):
        self.create_instrumentation_clients()

        service = self.app.extensions["clients"]

        with patch.object(
            service.tree,
            "list_all",
            side_effect=AssertionError(
                "Listagem indevida dos clientes"
            ),
        ) as listing:

            response = self.client.get(
                "/clients/instrumentation"
            )

            self.assertEqual(response.status_code, 200)

            listing.assert_not_called()

    def test_instrumentation_preserves_records_and_json(self):
        self.create_instrumentation_clients()
        self.create_coverage_country()

        service = self.app.extensions["clients"]

        records_before = service.list_all()
        stats_before = service.statistics()

        clients_before = self.clients_path.read_bytes()
        countries_before = self.countries_path.read_bytes()
        packages_before = self.packages_path.read_bytes()

        response = self.client.get(
            "/clients/instrumentation"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            service.list_all(),
            records_before,
        )

        self.assertEqual(
            service.statistics(),
            stats_before,
        )

        self.assertEqual(
            self.clients_path.read_bytes(),
            clients_before,
        )

        self.assertEqual(
            self.countries_path.read_bytes(),
            countries_before,
        )

        self.assertEqual(
            self.packages_path.read_bytes(),
            packages_before,
        )

if __name__ == "__main__":
    unittest.main()
