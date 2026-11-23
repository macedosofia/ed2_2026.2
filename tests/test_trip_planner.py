from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from globalsim.persistence import clients_json, countries_json, packages_json
from globalsim.services.clients import ClientService
from globalsim.services.countries import CountryService
from globalsim.services.packages import PackageService
from globalsim.services.trip_planner import TripPlannerService


DATA_PATH = Path(__file__).resolve().parents[1] / "globalsim" / "data"


class TripPlannerTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        base = Path(directory.name)
        self.countries_path = base / "countries.json"
        self.packages_path = base / "packages.json"
        self.clients_path = base / "clients.json"
        for path in (self.countries_path, self.packages_path):
            path.write_bytes((DATA_PATH / path.name).read_bytes())

        self.countries = CountryService(self.countries_path)
        self.packages = PackageService(self.packages_path)
        self.clients = ClientService(self.clients_path)
        self.planner = TripPlannerService(self.countries, self.packages, self.clients)

    def recommend(self, **overrides):
        trip = {
            "origin": "BR",
            "destinations": ["PT", "FR", "IT"],
            "duration_days": 25,
            "data_gb": 8,
        }
        trip.update(overrides)
        return self.planner.recommend(**trip)

    def test_rejects_invalid_origin(self):
        for origin in ("", "BRA", "1R", "ß", None):
            with self.subTest(origin=origin), self.assertRaisesRegex(ValueError, "origem"):
                self.recommend(origin=origin)

    def test_rejects_empty_or_unordered_destinations(self):
        for destinations in ([], (), "PT", {"PT", "FR"}, None):
            with self.subTest(destinations=destinations), self.assertRaisesRegex(
                ValueError, "pelo menos um destino"
            ):
                self.recommend(destinations=destinations)

    def test_rejects_invalid_destination_before_lookup(self):
        with patch.object(self.countries, "find", wraps=self.countries.find) as find:
            for code in ("", "FRA", "F1", 12):
                with self.subTest(code=code), self.assertRaisesRegex(ValueError, "destino"):
                    self.recommend(destinations=["PT", code])
            find.assert_not_called()

    def test_rejects_invalid_duration(self):
        for duration in (0, -1, "25", "vinte", 25.0, True, None):
            with self.subTest(duration=duration), self.assertRaisesRegex(ValueError, "duração"):
                self.recommend(duration_days=duration)

    def test_rejects_invalid_consumption(self):
        for consumption in (
            0, -1, True, "8", None, float("inf"), float("nan"),
            Decimal("NaN"), Decimal("sNaN"), Decimal("-Infinity"),
        ):
            with self.subTest(consumption=consumption), self.assertRaisesRegex(
                ValueError, "consumo"
            ):
                self.recommend(data_gb=consumption)

    def test_normalizes_country_codes_and_keeps_first_occurrence(self):
        lookups_before = self.countries.statistics()["lookups"]
        result = self.recommend(origin=" br ", destinations=[" fr ", "pt", "FR", " it "])

        self.assertEqual(result["origem"], "BR")
        self.assertEqual([country["codigo"] for country in result["destinos"]], ["FR", "PT", "IT"])
        self.assertEqual([country["pais"] for country in result["destinos"]], [
            "França", "Portugal", "Itália"
        ])
        self.assertTrue(all(country["cobertura"] for country in result["destinos"]))
        self.assertEqual(self.countries.statistics()["lookups"] - lookups_before, 3)

    def test_origin_with_valid_code_is_not_required_to_have_coverage(self):
        result = self.recommend(origin="de")

        self.assertEqual(result["origem"], "DE")
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)

    def test_recommends_europa_plus_and_explains_the_choice(self):
        result = self.recommend()

        self.assertEqual(result["status"], "recomendado")
        self.assertEqual(result["destinos_sem_cobertura"], [])
        self.assertEqual(result["pacote_recomendado"], self.packages.find(102))
        for detail in (
            "Europa Plus", "PT, FR, IT", "10 GB", "30 dias", "8 GB", "25 dias",
            "menor franquia suficiente", "menor validade excedente", "menor código",
        ):
            self.assertIn(detail, result["justificativa"])

    def test_recommends_global_for_an_intercontinental_trip(self):
        result = self.recommend(destinations=["PT", "US"], duration_days=20)

        self.assertEqual(result["pacote_recomendado"]["codigo"], 301)

    def test_missing_coverage_prevents_package_selection(self):
        with patch.object(self.packages, "list_all", wraps=self.packages.list_all) as list_all:
            result = self.recommend(destinations=["PT", "DE"])

        self.assertEqual(result["status"], "sem_cobertura")
        self.assertEqual(result["destinos_sem_cobertura"], ["DE"])
        self.assertEqual(result["destinos"][0], {
            "codigo": "PT", "pais": "Portugal", "cobertura": True,
        })
        self.assertEqual(result["destinos"][1], {
            "codigo": "DE", "pais": None, "cobertura": False,
        })
        self.assertIsNone(result["pacote_recomendado"])
        list_all.assert_not_called()

    def test_reports_all_destinations_without_coverage_in_order(self):
        result = self.recommend(destinations=["MX", "PT", "de", "mx"])

        self.assertEqual(result["destinos_sem_cobertura"], ["MX", "DE"])
        self.assertIn("MX, DE", result["justificativa"])
        self.assertIsNone(result["pacote_recomendado"])

    def test_rejects_packages_that_only_cover_part_of_the_route(self):
        catalog = [self.packages.find(102), self.packages.find(202)]
        with patch.object(self.packages, "list_all", return_value=catalog):
            result = self.recommend(destinations=["PT", "US"], duration_days=20)

        self.assertEqual(result["status"], "sem_pacote")
        self.assertIsNone(result["pacote_recomendado"])

    def test_rejects_packages_with_insufficient_validity(self):
        result = self.recommend(destinations=["JP"], duration_days=40, data_gb=5)

        self.assertEqual(result["status"], "sem_pacote")
        self.assertIsNone(result["pacote_recomendado"])
        self.assertIn("Nenhum pacote compatível", result["justificativa"])

    def test_rejects_packages_with_insufficient_data(self):
        result = self.recommend(destinations=["PT"], duration_days=10, data_gb=25)

        self.assertEqual(result["status"], "sem_pacote")
        self.assertIsNone(result["pacote_recomendado"])

    def test_accepts_validity_and_data_exactly_equal_to_the_trip(self):
        result = self.recommend(duration_days=15, data_gb=Decimal("5"))

        self.assertEqual(result["pacote_recomendado"]["codigo"], 101)

    def test_keeps_fractional_consumption(self):
        result = self.recommend(duration_days=15, data_gb=5.1)

        self.assertEqual(result["consumo_gb"], Decimal("5.1"))
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)
        self.assertIn("5,1 GB", result["justificativa"])

    def test_prioritizes_less_data_before_shorter_validity_and_lower_code(self):
        catalog = [self.package(11, 10, 10), self.package(22, 5, 30)]

        self.assertEqual(self.choose_from_catalog(catalog), 22)

    def test_breaks_data_tie_by_excess_validity(self):
        catalog = [self.package(11, 5, 30), self.package(22, 5, 15)]

        self.assertEqual(self.choose_from_catalog(catalog), 22)

    def test_breaks_remaining_tie_by_code_in_any_catalog_order(self):
        catalog = [self.package(22, 5, 15), self.package(11, 5, 15), self.package(33, 10, 10)]

        self.assertEqual(self.choose_from_catalog(catalog), 11)
        self.assertEqual(self.choose_from_catalog(catalog[::-1]), 11)

    def test_rejects_invalid_client_id_before_looking_up_destinations(self):
        with patch.object(self.countries, "find", wraps=self.countries.find) as find:
            for client_id in (0, -1, True, "58372", 1.5):
                with self.subTest(client_id=client_id), self.assertRaisesRegex(ValueError, "ID"):
                    self.recommend(client_id=client_id)
            find.assert_not_called()

    def test_skips_client_lookup_when_id_is_omitted(self):
        lookups_before = self.clients.statistics()["lookups"]
        result = self.recommend()

        self.assertEqual(result["status_cliente"], "nao_informado")
        self.assertIsNone(result["cliente"])
        self.assertIsNone(result["pacote_atual"])
        self.assertEqual(self.clients.statistics()["lookups"], lookups_before)

    def test_client_service_is_optional(self):
        self.planner = TripPlannerService(self.countries, self.packages)

        self.assertEqual(self.recommend()["pacote_recomendado"]["codigo"], 102)
        result = self.recommend(client_id=58372)
        self.assertEqual(result["status_cliente"], "consulta_indisponivel")
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)

    def test_recovers_client_through_b_tree_and_compares_current_package(self):
        client_id = self.create_client(esim="ESIM-83921", pacote=301, status="inativo")
        lookups_before = self.clients.statistics()["lookups"]
        result = self.recommend(client_id=client_id)

        self.assertEqual(self.clients.statistics()["lookups"] - lookups_before, 1)
        self.assertEqual(result["status_cliente"], "encontrado")
        self.assertEqual(result["cliente"]["nome"], "Maria Silva")
        self.assertEqual(result["cliente"]["esim"], "ESIM-83921")
        self.assertEqual(result["cliente"]["status"], "inativo")
        self.assertEqual(result["pacote_atual"], self.packages.find(301))
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)

    def test_reports_missing_client_and_keeps_recommendation(self):
        result = self.recommend(client_id=58372)

        self.assertEqual(result["cliente_id"], 58372)
        self.assertEqual(result["status_cliente"], "nao_encontrado")
        self.assertIsNone(result["cliente"])
        self.assertIsNone(result["pacote_atual"])
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)

    def test_handles_client_without_esim_or_associated_package(self):
        client_id = self.create_client()
        with patch.object(self.packages, "find", wraps=self.packages.find) as find:
            result = self.recommend(client_id=client_id)

        self.assertEqual(result["status_cliente"], "encontrado")
        self.assertIsNone(result["cliente"]["esim"])
        self.assertIsNone(result["cliente"]["pacote"])
        self.assertIsNone(result["pacote_atual"])
        find.assert_not_called()

    def test_handles_associated_package_missing_from_catalog(self):
        client_id = self.create_client(pacote=999)
        result = self.recommend(client_id=client_id)

        self.assertEqual(result["status_cliente"], "encontrado")
        self.assertEqual(result["cliente"]["pacote"], 999)
        self.assertIsNone(result["pacote_atual"])
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)

    def test_planning_leaves_records_and_json_untouched(self):
        client_id = self.create_client(pacote=101)
        paths = (self.countries_path, self.packages_path, self.clients_path)
        services = (self.countries, self.packages, self.clients)
        previous_contents = [path.read_bytes() for path in paths]
        previous_records = [service.list_all() for service in services]
        unexpected_access = AssertionError("A consulta tentou acessar a persistência.")
        with (
            patch.object(countries_json, "load", side_effect=unexpected_access),
            patch.object(countries_json, "save", side_effect=unexpected_access),
            patch.object(packages_json, "load", side_effect=unexpected_access),
            patch.object(clients_json, "load", side_effect=unexpected_access),
            patch.object(clients_json, "save", side_effect=unexpected_access),
        ):
            result = self.recommend(client_id=client_id)

        self.assertEqual(result["pacote_atual"]["codigo"], 101)
        self.assertEqual(result["pacote_recomendado"]["codigo"], 102)
        self.assertEqual([path.read_bytes() for path in paths], previous_contents)
        self.assertEqual([service.list_all() for service in services], previous_records)

    def create_client(self, **overrides):
        record = {
            "id": 58372,
            "nome": "Maria Silva",
            "email": "maria@example.com",
            "esim": None,
            "pacote": None,
            "status": "ativo",
        }
        record.update(overrides)
        self.clients.create(record)
        return record["id"]

    def package(self, code, data_gb, days):
        return {
            "codigo": code,
            "nome": f"Teste {code}",
            "dados_gb": data_gb,
            "validade_dias": days,
            "paises": ["PT"],
        }

    def choose_from_catalog(self, catalog):
        with patch.object(self.packages, "list_all", return_value=catalog):
            result = self.recommend(destinations=["PT"], duration_days=10, data_gb=5)
        return result["pacote_recomendado"]["codigo"]
