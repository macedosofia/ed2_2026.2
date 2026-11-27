import unittest
from copy import deepcopy
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

    def assert_consistent_index(self, service):
        self.assertEqual(
            len(service.clients),
            service.statistics()["size"]
        )

        for position, client in enumerate(service.clients):
            self.assertEqual(
                service.tree._find_node(
                    service.tree.root,
                    client["id"]
                ),
                position
            )

        expected_positions = sorted(
            range(len(service.clients)),
            key=lambda position: service.clients[position]["id"]
        )

        self.assertEqual(
            service.tree.list_all(),
            expected_positions
        )

    def test_empty_service(self):
        self.assertEqual(self.service.clients, [])
        self.assertEqual(self.service.list_all(), [])
        self.assertEqual(self.service.statistics()["size"], 0)
        self.assertFalse(self.path.exists())

        self.assert_consistent_index(self.service)

    def test_load_existing_clients(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)

        service = ClientService(self.path)

        self.assertEqual(service.clients, records)
        self.assertEqual(service.statistics()["size"], 3)

        self.assertEqual(
            service.tree.root.keys,
            [10, 20, 30]
        )

        self.assertEqual(
            service.tree.root.positions,
            [1, 2, 0]
        )

        self.assertEqual(
            [client["id"] for client in service.list_all()],
            [10, 20, 30],
        )

        self.assert_consistent_index(service)

    def test_find_existing_client(self):
        client = self.make_client(1)

        self.service.create(client)

        self.assertEqual(self.service.find(1), client)

    def test_find_client_at_position_zero(self):
        client = self.make_client(30)

        self.service.create(client)
        self.service.create(self.make_client(10))

        self.assertEqual(self.service.tree.find(30), 0)
        self.assertEqual(self.service.find(30), client)

    def test_find_missing_client(self):
        self.assertIsNone(self.service.find(999))

    def test_find_invalid_id(self):
        for client_id in [0, -1, True, "1", None]:
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    self.service.find(client_id)

    def test_find_uses_btree_position(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)

        service = ClientService(self.path)

        with patch.object(
            service.tree,
            "find",
            wraps=service.tree.find,
        ) as tree_find:

            result = service.find(20)

            tree_find.assert_called_once_with(20)
            self.assertEqual(result, records[2])

    def test_find_accesses_position_returned_by_tree(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)

        service = ClientService(self.path)

        with patch.object(
            service.tree,
            "find",
            return_value=2,
        ) as tree_find:

            result = service.find(999)

            tree_find.assert_called_once_with(999)
            self.assertEqual(result, records[2])

    def test_find_does_not_list_all_records(self):
        self.service.create(self.make_client(1))

        with patch.object(
            self.service.tree,
            "list_all",
            side_effect=AssertionError(
                "Listagem desnecessaria"
            ),
        ) as listing:

            self.assertEqual(
                self.service.find(1),
                self.make_client(1)
            )

            listing.assert_not_called()

    def test_create_and_persist(self):
        client = self.make_client(1)

        self.service.create(client)

        self.assertTrue(self.path.exists())

        self.assertEqual(
            clients_json.load(self.path),
            [client]
        )

        self.assertEqual(self.service.clients, [client])
        self.assertEqual(self.service.tree.find(1), 0)

        self.assert_consistent_index(self.service)

    def test_create_appends_without_moving_existing_records(self):
        self.service.create(self.make_client(30))
        self.service.create(self.make_client(10))
        self.service.create(self.make_client(20))

        self.assertEqual(
            [client["id"] for client in self.service.clients],
            [30, 10, 20]
        )

        self.assertEqual(self.service.tree.find(30), 0)
        self.assertEqual(self.service.tree.find(10), 1)
        self.assertEqual(self.service.tree.find(20), 2)

        self.service.create(self.make_client(5))

        self.assertEqual(self.service.tree.find(30), 0)
        self.assertEqual(self.service.tree.find(10), 1)
        self.assertEqual(self.service.tree.find(20), 2)
        self.assertEqual(self.service.tree.find(5), 3)

        self.assertEqual(
            [client["id"] for client in self.service.clients],
            [30, 10, 20, 5]
        )

        self.assert_consistent_index(self.service)

    def test_list_all_preserves_array_order(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)

        service = ClientService(self.path)

        listed = service.list_all()

        self.assertEqual(
            [client["id"] for client in listed],
            [10, 20, 30]
        )

        self.assertEqual(service.clients, records)

        self.assert_consistent_index(service)

    def test_list_all_uses_btree_traversal(self):
        self.service.create(self.make_client(30))
        self.service.create(self.make_client(10))
        self.service.create(self.make_client(20))

        with patch.object(
            self.service.tree,
            "list_all",
            wraps=self.service.tree.list_all,
        ) as tree_listing:

            listed = self.service.list_all()

            tree_listing.assert_called_once_with()

            self.assertEqual(
                [client["id"] for client in listed],
                [10, 20, 30]
            )

    def test_persistence_preserves_array_order(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        for client in records:
            self.service.create(client)

        self.assertEqual(
            clients_json.load(self.path),
            records
        )

        self.assertEqual(self.service.clients, records)

    def test_restart_recovers_clients(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        for client in records:
            self.service.create(client)

        new_service = ClientService(self.path)

        self.assertEqual(new_service.clients, records)

        for position, client in enumerate(records):
            self.assertEqual(
                new_service.find(client["id"]),
                client
            )

            self.assertEqual(
                new_service.tree.find(client["id"]),
                position
            )

        self.assert_consistent_index(new_service)

    def test_duplicate_id_preserves_state(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        duplicate = dict(client, nome="Outro Cliente")

        with self.assertRaises(ValueError):
            self.service.create(duplicate)

        self.assertEqual(self.service.clients, [client])
        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

        self.assert_consistent_index(self.service)

    def test_invalid_client_preserves_state(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        invalid = dict(
            self.make_client(2),
            email="invalido"
        )

        with self.assertRaises(ValueError):
            self.service.create(invalid)

        self.assertEqual(self.service.clients, [client])
        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

        self.assert_consistent_index(self.service)

    def test_rollback_on_save_failure(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()
        original_clients = deepcopy(self.service.clients)
        original_positions = self.service.tree.list_all()

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            with self.assertRaises(OSError):
                self.service.create(self.make_client(2))

        self.assertEqual(
            self.service.clients,
            original_clients
        )

        self.assertEqual(
            self.service.tree.list_all(),
            original_positions
        )

        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

        self.assertIsNone(self.service.find(2))

        self.assert_consistent_index(self.service)

    def test_rollback_restores_tree_after_split(self):
        ids = [30, 10, 20, 50, 40]

        for client_id in ids:
            self.service.create(
                self.make_client(client_id)
            )

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        original_clients = deepcopy(self.service.clients)
        original_keys = self.service.tree.root.keys.copy()
        original_positions = (
            self.service.tree.root.positions.copy()
        )

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            with self.assertRaises(OSError):
                self.service.create(self.make_client(60))

        self.assertEqual(
            self.service.clients,
            original_clients
        )

        self.assertEqual(
            self.service.tree.root.keys,
            original_keys
        )

        self.assertEqual(
            self.service.tree.root.positions,
            original_positions
        )

        self.assertTrue(self.service.tree.root.leaf)
        self.assertEqual(self.service.tree.root.children, [])

        self.assertEqual(
            self.service.statistics(),
            statistics
        )

        self.assertEqual(
            self.path.read_bytes(),
            original
        )

        self.assertIsNone(self.service.find(60))

        self.assert_consistent_index(self.service)

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

        self.assertEqual(
            self.service.clients[0]["nome"],
            "Cliente 1"
        )

    def test_operations_do_not_reload_json(self):
        self.service.create(self.make_client(1))

        with patch(
            "globalsim.services.clients.clients_json.load",
            side_effect=AssertionError(
                "Leitura desnecessaria"
            ),
        ):
            self.service.find(1)
            self.service.list_all()
            self.service.statistics()
            self.service.create(self.make_client(2))

            self.service.update(
                1,
                {"nome": "Nome atualizado"}
            )

        self.assertEqual(
            self.service.statistics()["size"],
            2
        )

        self.assert_consistent_index(self.service)

    def test_load_duplicate_ids(self):
        clients_json.save(
            self.path,
            [
                self.make_client(1),
                self.make_client(1)
            ],
        )

        original = self.path.read_bytes()

        with self.assertRaises(ValueError):
            ClientService(self.path)

        self.assertEqual(
            self.path.read_bytes(),
            original
        )

    def test_load_invalid_client(self):
        invalid = dict(
            self.make_client(1),
            email="invalido"
        )

        clients_json.save(self.path, [invalid])

        original = self.path.read_bytes()

        with self.assertRaises(ValueError):
            ClientService(self.path)

        self.assertEqual(
            self.path.read_bytes(),
            original
        )

    def test_load_does_not_rewrite_json(self):
        records = [
            self.make_client(30),
            self.make_client(10),
            self.make_client(20),
        ]

        clients_json.save(self.path, records)

        original = self.path.read_bytes()

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=AssertionError(
                "Gravacao desnecessaria"
            ),
        ) as saver:

            service = ClientService(self.path)

            saver.assert_not_called()

        self.assertEqual(
            self.path.read_bytes(),
            original
        )

        self.assert_consistent_index(service)

    def test_load_one_thousand_clients(self):
        records = [
            self.make_client(i)
            for i in range(1000, 0, -1)
        ]

        clients_json.save(self.path, records)

        service = ClientService(self.path)

        self.assertEqual(len(service.clients), 1000)
        self.assertEqual(service.clients, records)

        self.assertEqual(
            service.statistics()["size"],
            1000
        )

        self.assertGreater(
            service.statistics()["height"],
            1
        )

        self.assertGreater(
            service.statistics()["splits"],
            0
        )

        self.assertEqual(
            [client["id"] for client in service.list_all()],
            list(range(1, 1001)),
        )

        for position, client in enumerate(records):
            self.assertEqual(
                service.tree.find(client["id"]),
                position
            )

            self.assertEqual(
                service.find(client["id"]),
                client
            )

        self.assertEqual(
            service.find(500),
            self.make_client(500),
        )

        self.assertIsNone(service.find(1001))

        self.assert_consistent_index(service)

    def test_partial_update(self):
        client = self.make_client(1)

        self.service.create(client)

        self.service.update(
            1,
            {"nome": "Novo Nome"}
        )

        expected = dict(
            client,
            nome="Novo Nome"
        )

        self.assertEqual(
            self.service.find(1),
            expected
        )

        self.assertEqual(
            self.service.clients[0],
            expected
        )

        self.assert_consistent_index(self.service)

    def test_update_preserves_client_position(self):
        ids = [30, 10, 20, 50, 40, 60]

        for client_id in ids:
            self.service.create(
                self.make_client(client_id)
            )

        original_positions = {
            client_id: self.service.tree.find(client_id)
            for client_id in ids
        }

        original_stats = self.service.statistics()

        for client_id in [30, 40]:
            with self.subTest(client_id=client_id):
                updated = {
                    "nome": "Nome atualizado"
                }

                self.service.update(client_id, updated)

                updated["nome"] = "Alterado externamente"

                self.assertEqual(
                    self.service.find(client_id)["nome"],
                    "Nome atualizado"
                )

                position = original_positions[client_id]

                self.assertEqual(
                    self.service.clients[position]["nome"],
                    "Nome atualizado"
                )

        for client_id in ids:
            self.assertEqual(
                self.service.tree.find(client_id),
                original_positions[client_id]
            )

        current_stats = self.service.statistics()

        for field in [
            "size",
            "height",
            "node_count",
            "splits"
        ]:
            self.assertEqual(
                current_stats[field],
                original_stats[field]
            )

        self.assertEqual(
            [client["id"] for client in self.service.list_all()],
            sorted(ids)
        )

        self.assert_consistent_index(self.service)

    def test_update_does_not_reinsert_key(self):
        self.service.create(self.make_client(1))

        with patch.object(
            self.service.tree,
            "insert",
            side_effect=AssertionError(
                "Reinsercao desnecessaria"
            ),
        ) as tree_insert:

            self.service.update(
                1,
                {"nome": "Novo Nome"}
            )

            tree_insert.assert_not_called()

        self.assertEqual(
            self.service.find(1)["nome"],
            "Novo Nome"
        )

        self.assert_consistent_index(self.service)

    def test_update_persistence(self):
        self.service.create(self.make_client(1))

        self.service.update(
            1,
            {"status": "inativo"}
        )

        new_service = ClientService(self.path)

        self.assertEqual(
            new_service.find(1)["status"],
            "inativo",
        )

        self.assertEqual(
            new_service.tree.find(1),
            0
        )

        self.assert_consistent_index(new_service)

    def test_associate_esim_and_package(self):
        client = self.make_client(1)

        self.service.create(client)

        self.service.update(
            1,
            {
                "esim": "ESIM001",
                "pacote": 10
            }
        )

        expected = dict(
            client,
            esim="ESIM001",
            pacote=10
        )

        self.assertEqual(
            self.service.find(1),
            expected
        )

        self.assertEqual(
            clients_json.load(self.path),
            [expected]
        )

        self.assert_consistent_index(self.service)

    def test_update_cannot_change_id(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        with self.assertRaises(ValueError):
            self.service.update(
                1,
                {"id": 2}
            )

        self.assertEqual(self.service.clients, [client])
        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

        self.assertEqual(self.service.tree.find(1), 0)
        self.assertIsNone(self.service.find(2))

        self.assert_consistent_index(self.service)

    def test_update_missing_client(self):
        statistics = self.service.statistics()

        with self.assertRaises(LookupError):
            self.service.update(
                999,
                {"nome": "Novo Nome"}
            )

        self.assertEqual(self.service.clients, [])
        self.assertEqual(self.service.list_all(), [])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertFalse(self.path.exists())

        self.assert_consistent_index(self.service)

    def test_update_invalid_data(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        invalid_changes = [
            {"email": "invalido"},
            {"nome": ""},
            {"pacote": -1},
            {"esim": ""},
            {"status": ""},
            {"id": True},
        ]

        for changes in invalid_changes:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.service.update(1, changes)

                self.assertEqual(
                    self.service.clients,
                    [client]
                )

                self.assertEqual(
                    self.service.list_all(),
                    [client]
                )

                self.assertEqual(
                    self.service.statistics(),
                    statistics
                )

                self.assertEqual(
                    self.path.read_bytes(),
                    original
                )

                self.assert_consistent_index(self.service)

    def test_update_unknown_field(self):
        client = self.make_client(1)

        self.service.create(client)

        with self.assertRaises(ValueError):
            self.service.update(
                1,
                {"campo_invalido": "valor"}
            )

        self.assertEqual(self.service.list_all(), [client])

        self.assert_consistent_index(self.service)

    def test_update_invalid_changes_type(self):
        client = self.make_client(1)

        self.service.create(client)

        for changes in [None, [], "invalido", 10]:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.service.update(1, changes)

        self.assertEqual(self.service.list_all(), [client])

        self.assert_consistent_index(self.service)

    def test_update_rollback_on_save_failure(self):
        client = self.make_client(1)

        self.service.create(client)

        original = self.path.read_bytes()
        statistics = self.service.statistics()

        original_clients = deepcopy(self.service.clients)
        original_positions = self.service.tree.list_all()

        with patch(
            "globalsim.services.clients.clients_json.save",
            side_effect=OSError("Falha simulada"),
        ):
            with self.assertRaises(OSError):
                self.service.update(
                    1,
                    {"nome": "Novo Nome"}
                )

        self.assertEqual(
            self.service.clients,
            original_clients
        )

        self.assertEqual(
            self.service.tree.list_all(),
            original_positions
        )

        self.assertEqual(self.service.list_all(), [client])
        self.assertEqual(self.service.statistics(), statistics)
        self.assertEqual(self.path.read_bytes(), original)

        self.assert_consistent_index(self.service)


if __name__ == "__main__":
    unittest.main()