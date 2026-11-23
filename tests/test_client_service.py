
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from globalsim.persistence import clients_json
from globalsim.services.clients import ClientService


class TestClientService(unittest.TestCase):

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "clients.json"
        self.service = ClientService(self.path)

    def make_client(self, client_id):
        return {
            "id": client_id,
            "nome": f"Cliente {client_id}",
            "email": f"cliente{client_id}@email.com",
            "esim": None,
            "pacote": None,
            "status": "ativo",
        }

    def test_empty_service(self):
        self.assertEqual(self.service.list_all(), [])
        self.assertEqual(self.service.statistics()["size"], 0)
        self.assertFalse(self.path.exists())

    def test_load_existing_clients(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)
        service = ClientService(self.path)

        self.assertEqual(service.statistics()["size"], 3)
        self.assertEqual(
            [client["id"] for client in service.list_all()],
            [10, 20, 30],
        )

    def test_find_existing_client(self):
        client = self.make_client(1)
        self.service.create(client)

        self.assertEqual(self.service.find(1), client)

    def test_find_missing_client(self):
        self.assertIsNone(self.service.find(999))

    def test_find_invalid_id(self):
        for client_id in [0, -1, True, "1", None]:
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    self.service.find(client_id)

    def test_create_and_persist(self):
        client = self.make_client(1)
        self.service.create(client)

        self.assertTrue(self.path.exists())
        self.assertEqual(clients_json.load(self.path), [client])

    def test_restart_recovers_clients(self):
        client = self.make_client(1)
        self.service.create(client)

        new_service = ClientService(self.path)

        self.assertEqual(new_service.find(1), client)

    def test_duplicate_id_preserves_state(self):
        client = self.make_client(1)
        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        duplicate = dict(client, nome="Outro Cliente")

        with self.assertRaises(ValueError):
            self.service.create(duplicate)

        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_client_preserves_state(self):
        client = self.make_client(1)
        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        invalid = dict(self.make_client(2), email="invalido")

        with self.assertRaises(ValueError):
            self.service.create(invalid)

        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

    def test_rollback_on_save_failure(self):
        client = self.make_client(1)
        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            with self.assertRaises(OSError):
                self.service.create(self.make_client(2))

        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

    def test_independent_records(self):
        client = self.make_client(1)
        self.service.create(client)

        client["nome"] = "Nome alterado"

        found = self.service.find(1)
        found["nome"] = "Outra alteracao"

        listed = self.service.list_all()
        listed[0]["nome"] = "Mais uma alteracao"

        self.assertEqual(
            self.service.find(1)["nome"],
            "Cliente 1",
        )

    def test_operations_do_not_reload_json(self):
        self.service.create(self.make_client(1))

        with patch(
            "globalsim.services.clients.clients_json.load",
            side_effect=AssertionError("Leitura desnecessaria"),
        ):
            self.service.find(1)
            self.service.list_all()
            self.service.statistics()
            self.service.create(self.make_client(2))

        self.assertEqual(self.service.statistics()["size"], 2)

    def test_load_duplicate_ids(self):
        clients_json.save(
            self.path,
            [self.make_client(1), self.make_client(1)],
        )

        original = self.path.read_bytes()

        with self.assertRaises(ValueError):
            ClientService(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_load_invalid_client(self):
        invalid = dict(self.make_client(1), email="invalido")
        clients_json.save(self.path, [invalid])

        original = self.path.read_bytes()

        with self.assertRaises(ValueError):
            ClientService(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_load_one_thousand_clients(self):
        records = [
            self.make_client(i)
            for i in range(1000, 0, -1)
        ]

        clients_json.save(self.path, records)
        service = ClientService(self.path)

        self.assertEqual(service.statistics()["size"], 1000)
        self.assertGreater(service.statistics()["height"], 1)
        self.assertGreater(service.statistics()["splits"], 0)

        self.assertEqual(
            [client["id"] for client in service.list_all()],
            list(range(1, 1001)),
        )

        self.assertEqual(
            service.find(500),
            self.make_client(500),
        )


if __name__ == "__main__":
    unittest.main()
