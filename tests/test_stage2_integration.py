from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from globalsim.app import create_app


DATA_PATH = Path(__file__).resolve().parents[1] / "globalsim" / "data"


class Stage2IntegrationTests(TestCase):

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)

        base = Path(directory.name)

        self.countries_path = base / "countries.json"
        self.packages_path = base / "packages.json"
        self.clients_path = base / "clients.json"

        for path in (self.countries_path, self.packages_path):
            path.write_bytes((DATA_PATH / path.name).read_bytes())

        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test",
                "COUNTRIES_PATH": self.countries_path,
                "PACKAGES_PATH": self.packages_path,
                "CLIENTS_PATH": self.clients_path,
            }
        )

        self.web = self.app.test_client()

    def test_planner_is_registered_and_accessible(self):
        self.assertIn("trip_planner", self.app.blueprints)

        response = self.web.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/trip-planner"', response.text)

        response = self.web.get("/trip-planner")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Planejador multidestinos", response.text)

    def test_planner_recommends_package_through_flask(self):
        response = self.web.post(
            "/trip-planner",
            data={
                "origin": "BR",
                "destinations": "PT, FR, IT",
                "duration_days": "25",
                "data_gb": "8",
                "client_id": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Europa Plus (102)", response.text)
        self.assertIn("10 GB", response.text)
        self.assertIn("30 dias", response.text)

    def test_planner_uses_shared_country_service(self):
        country = {
            "codigo": "DE",
            "pais": "Alemanha",
            "regiao": "Europa",
            "operadora": "Operadora Teste",
            "tecnologia": "5G",
        }

        countries = self.app.extensions["countries"]
        countries.create(country)

        lookups_before = countries.statistics()["lookups"]

        response = self.web.post(
            "/trip-planner",
            data={
                "origin": "BR",
                "destinations": "DE",
                "duration_days": "10",
                "data_gb": "5",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Alemanha", response.text)
        self.assertIn("Nenhum pacote compatível", response.text)

        self.assertEqual(
            countries.statistics()["lookups"] - lookups_before,
            1,
        )

    def test_planner_finds_client_created_through_web(self):
        client_data = {
            "id": "58372",
            "nome": "Maria Silva",
            "email": "maria@example.com",
            "esim": "ESIM-83921",
            "pacote": "101",
            "status": "ativo",
        }

        create_response = self.web.post(
            "/clients/new",
            data=client_data,
        )

        self.assertEqual(create_response.status_code, 303)

        clients = self.app.extensions["clients"]

        lookups_before = clients.statistics()["lookups"]
        json_before = self.clients_path.read_bytes()

        response = self.web.post(
            "/trip-planner",
            data={
                "origin": "BR",
                "destinations": "PT, FR, IT",
                "duration_days": "25",
                "data_gb": "8",
                "client_id": "58372",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("Maria Silva", response.text)
        self.assertIn("ESIM-83921", response.text)

        self.assertIn("Europa Basic (101)", response.text)
        self.assertIn("Europa Plus (102)", response.text)

        self.assertEqual(
            clients.statistics()["lookups"] - lookups_before,
            1,
        )

        self.assertEqual(
            self.clients_path.read_bytes(),
            json_before,
        )

        self.assertEqual(
            clients.find(58372)["pacote"],
            101,
        )