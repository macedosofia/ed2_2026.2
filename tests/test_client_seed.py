import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from globalsim.app import create_app
from globalsim.models.client import validate_client
from globalsim.persistence import clients_json
from globalsim.services.clients import ClientService
from globalsim.services.packages import PackageService
from scripts.generate_clients_demo import (
    DEFAULT_COUNT,
    DEFAULT_OUTPUT,
    DEFAULT_SEED,
    DEMO_FILENAME,
    DEMO_NAMES,
    generate_clients,
    generate_demo,
    validate_clients,
)


class ClientSeedTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = generate_clients()
        cls.committed = clients_json.load(DEFAULT_OUTPUT)

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.path = self.directory / DEMO_FILENAME

    def test_default_count_and_unique_positive_ids(self):
        ids = [client["id"] for client in self.generated]
        self.assertEqual(len(ids), 1_000)
        self.assertTrue(all(type(client_id) is int for client_id in ids))
        self.assertEqual(sorted(ids), list(range(1, DEFAULT_COUNT + 1)))
        self.assertNotEqual(ids, sorted(ids))

    def test_records_match_model_and_use_demo_contacts(self):
        emails = set()
        esims = set()
        for client in self.generated:
            with self.subTest(client_id=client["id"]):
                self.assertEqual(client, validate_client(client))
                self.assertRegex(client["email"], r"^cliente[0-9]{4}@example\.test$")
                emails.add(client["email"])
                if client["esim"] is not None:
                    self.assertRegex(client["esim"], r"^ESIM-[0-9]{5}$")
                    esims.add(client["esim"])
                else:
                    self.assertIsNone(client["pacote"])
                self.assertIn(client["status"], ("ativo", "inativo"))
        self.assertEqual(len(emails), DEFAULT_COUNT)
        self.assertEqual(len(esims), 800)
        self.assertEqual({client["status"] for client in self.generated}, {"ativo", "inativo"})

    def test_package_assignments_use_the_current_catalog(self):
        catalog = {package["codigo"] for package in PackageService().list_all()}
        assigned = {client["pacote"] for client in self.generated}
        self.assertEqual(assigned, catalog | {None})

    def test_names_are_assigned_in_id_order(self):
        by_id = sorted(self.generated, key=lambda client: client["id"])
        self.assertEqual(tuple(client["nome"] for client in by_id[:len(DEMO_NAMES)]), DEMO_NAMES)
        additional = {client["nome"] for client in by_id[len(DEMO_NAMES):]}
        self.assertEqual(len(additional), 300)
        self.assertTrue(additional.isdisjoint(DEMO_NAMES))

    def test_same_seed_reproduces_records_and_other_seed_changes_insertion_order(self):
        self.assertEqual(self.generated, generate_clients(count=DEFAULT_COUNT, seed=DEFAULT_SEED))
        changed = generate_clients(count=DEFAULT_COUNT, seed=DEFAULT_SEED + 1)
        self.assertNotEqual(self.generated, changed)
        self.assertEqual(
            sorted(self.generated, key=lambda client: client["id"]),
            sorted(changed, key=lambda client: client["id"]),
        )

    def test_rejects_invalid_counts_and_seeds(self):
        for count in (0, -1, True, "10", 10.0, None):
            with self.subTest(count=count), self.assertRaises(ValueError):
                generate_clients(count=count)
        for seed in (True, "2026", None):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                generate_clients(count=1, seed=seed)

    def test_batch_validation_rejects_duplicate_ids_and_invalid_records(self):
        client = self.generated[0]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validate_clients([client, dict(client)])
        with self.assertRaisesRegex(ValueError, "E-mail"):
            validate_clients([dict(client, email="invalido")])

    def test_generation_reproduces_the_checked_in_file_byte_for_byte(self):
        stats = generate_demo(self.path)
        self.assertEqual(stats["size"], DEFAULT_COUNT)
        self.assertEqual(self.path.read_bytes(), DEFAULT_OUTPUT.read_bytes())
        self.assertEqual(clients_json.load(self.path), self.generated)
        self.assertEqual(ClientService(self.path).statistics(), stats)

    def test_existing_file_requires_explicit_replacement(self):
        self.path.write_bytes(b"conteudo original")
        with self.assertRaises(FileExistsError):
            generate_demo(self.path, count=4)
        self.assertEqual(self.path.read_bytes(), b"conteudo original")
        generate_demo(self.path, count=4, replace=True)
        self.assertEqual(clients_json.load(self.path), generate_clients(count=4))

    def test_original_data_files_are_protected_even_with_replace(self):
        for filename in ("clients.json", "countries.json", "packages.json", "countries.demo.json"):
            path = self.directory / filename
            path.write_bytes(b"[]")
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                generate_demo(path, count=1, replace=True)
            self.assertEqual(path.read_bytes(), b"[]")

    def test_rejects_symlink_to_the_normal_client_database(self):
        actual = self.directory / "clients.json"
        actual.write_bytes(b"[]")
        try:
            self.path.symlink_to(actual)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Links simbólicos indisponíveis: {error}")
        with self.assertRaises(ValueError):
            generate_demo(self.path, count=1, replace=True)
        self.assertTrue(self.path.is_symlink())
        self.assertEqual(actual.read_bytes(), b"[]")

    def test_concurrent_creation_does_not_overwrite_the_first_file(self):
        records = generate_clients(count=1)

        def concurrent_creation(count, seed):
            self.path.write_bytes(b"[]")
            return records

        with patch("scripts.generate_clients_demo.generate_clients", side_effect=concurrent_creation):
            with self.assertRaises(FileExistsError):
                generate_demo(self.path, count=1)
        self.assertEqual(self.path.read_bytes(), b"[]")

    def test_failed_tree_load_preserves_previous_file(self):
        self.path.write_bytes(b"[]")
        client = self.generated[0]
        with patch("scripts.generate_clients_demo.generate_clients", return_value=[client, client]):
            with self.assertRaises(ValueError):
                generate_demo(self.path, count=2, replace=True)
        self.assertEqual(self.path.read_bytes(), b"[]")

    def test_checked_in_data_loads_the_b_tree_and_supports_queries(self):
        before = DEFAULT_OUTPUT.read_bytes()
        service = ClientService(DEFAULT_OUTPUT)
        expected = sorted(self.committed, key=lambda client: client["id"])
        stats = service.statistics()
        self.assertEqual(stats["size"], DEFAULT_COUNT)
        self.assertGreater(stats["height"], 1)
        self.assertGreater(stats["node_count"], 1)
        self.assertGreater(stats["splits"], 0)
        self.assertEqual(service.list_all(), expected)
        for index in (0, 499, 999):
            self.assertEqual(service.find(expected[index]["id"]), expected[index])
        self.assertIsNone(service.find(DEFAULT_COUNT + 1))
        self.assertEqual(service.statistics()["lookups"], stats["lookups"] + 4)
        self.assertEqual(DEFAULT_OUTPUT.read_bytes(), before)

    def test_flask_loads_the_demonstration_from_configured_path(self):
        shutil.copyfile(DEFAULT_OUTPUT, self.path)
        app = create_app({"TESTING": True, "CLIENTS_PATH": self.path})
        service = app.extensions["clients"]
        self.assertEqual(service.statistics()["size"], DEFAULT_COUNT)
        self.assertEqual(len(service.list_all()), DEFAULT_COUNT)
        self.assertEqual(service.find(1)["id"], 1)
