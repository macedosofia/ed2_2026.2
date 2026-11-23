from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from globalsim.app import create_app
from globalsim.routes.trip_planner import create_trip_planner_blueprint
from globalsim.services.clients import ClientService
from globalsim.services.packages import PackageService
from globalsim.services.trip_planner import TripPlannerService


DATA_PATH = Path(__file__).resolve().parents[1] / "globalsim" / "data"


class TripPlannerRoutesTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        base = Path(directory.name)
        countries_path = base / "countries.json"
        packages_path = base / "packages.json"
        for path in (countries_path, packages_path):
            path.write_bytes((DATA_PATH / path.name).read_bytes())

        app = create_app({"TESTING": True, "COUNTRIES_PATH": countries_path})
        self.clients = ClientService(base / "clients.json")
        planner = TripPlannerService(
            app.extensions["countries"], PackageService(packages_path), self.clients
        )
        app.register_blueprint(create_trip_planner_blueprint(planner))
        self.web = app.test_client()

    def post_trip(self, **overrides):
        trip = {
            "origin": "BR",
            "destinations": "PT, FR, IT",
            "duration_days": "25",
            "data_gb": "8",
            "client_id": "",
        }
        trip.update(overrides)
        return self.web.post("/trip-planner", data=trip)

    def test_get_displays_the_planning_form(self):
        response = self.web.get("/trip-planner")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Planejador multidestinos", response.text)
        self.assertIn('method="post" action="/trip-planner"', response.text)
        for field in ("origin", "destinations", "duration_days", "data_gb", "client_id"):
            self.assertIn(f'name="{field}"', response.text)

    def test_post_recommends_a_package_for_the_full_route(self):
        response = self.post_trip(origin=" br ", destinations=" pt , FR, it, PT ")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Europa Plus (102)", response.text)
        self.assertIn("Portugal", response.text)
        self.assertIn("Itália", response.text)
        self.assertIn("10 GB", response.text)
        self.assertIn("30 dias", response.text)
        self.assertIn("menor franquia suficiente", response.text)
        self.assertNotIn('<h2 id="client">', response.text)

    def test_post_accepts_comma_and_dot_for_decimal_consumption(self):
        for data_gb in ("5,1", "5.1"):
            with self.subTest(data_gb=data_gb):
                response = self.post_trip(duration_days="15", data_gb=data_gb)

                self.assertEqual(response.status_code, 200)
                self.assertIn("5,1 GB", response.text)
                self.assertIn("Europa Plus (102)", response.text)

    def test_post_returns_bad_request_for_invalid_input(self):
        cases = (
            ({"origin": "Brasil"}, "A origem"),
            ({"destinations": ""}, "pelo menos um destino"),
            ({"destinations": "PT,,FR"}, "Cada destino"),
            ({"duration_days": "texto"}, "A duração"),
            ({"duration_days": "-2"}, "A duração"),
            ({"duration_days": "1.5"}, "A duração"),
            ({"data_gb": "texto"}, "O consumo"),
            ({"data_gb": "NaN"}, "O consumo"),
            ({"data_gb": "Infinity"}, "O consumo"),
            ({"client_id": "zero"}, "O ID"),
            ({"client_id": "0"}, "O ID"),
        )
        for overrides, message in cases:
            with self.subTest(overrides=overrides):
                response = self.post_trip(**overrides)

                self.assertEqual(response.status_code, 400)
                self.assertIn('role="alert"', response.text)
                self.assertIn(message, response.text)
                self.assertNotIn("Pacote recomendado", response.text)

    def test_post_reports_uncovered_destinations(self):
        response = self.post_trip(destinations="PT, DE, MX")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sem cobertura cadastrada em DE, MX.", response.text)
        self.assertNotIn("Pacote recomendado", response.text)

    def test_post_reports_no_compatible_package(self):
        response = self.post_trip(destinations="JP", duration_days="40")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nenhum pacote compatível", response.text)
        self.assertNotIn("Pacote recomendado", response.text)

    def test_post_shows_current_and_recommended_packages(self):
        self.create_client()
        response = self.post_trip(client_id=" 58372 ")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Maria Silva", response.text)
        self.assertIn("ESIM-83921", response.text)
        self.assertIn("Europa Basic (101)", response.text)
        self.assertIn("Europa Plus (102)", response.text)
        self.assertEqual(self.clients.find(58372)["pacote"], 101)

    def test_post_reports_unknown_client_and_shows_recommendation(self):
        response = self.post_trip(client_id="58372")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cliente 58372 não encontrado.", response.text)
        self.assertIn("Europa Plus (102)", response.text)

    def test_post_shows_missing_current_package_for_a_known_client(self):
        self.create_client(pacote=999)
        response = self.post_trip(client_id="58372")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Pacote 999 indisponível no catálogo.", response.text)
        self.assertIn("Europa Plus (102)", response.text)

    def test_post_shows_client_without_package_or_esim(self):
        self.create_client(pacote=None, esim=None)
        response = self.post_trip(client_id="58372")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sem pacote associado.", response.text)
        self.assertIn("Sem eSIM associado", response.text)

    def create_client(self, **overrides):
        record = {
            "id": 58372,
            "nome": "Maria Silva",
            "email": "maria@example.com",
            "esim": "ESIM-83921",
            "pacote": 101,
            "status": "ativo",
        }
        record.update(overrides)
        self.clients.create(record)
