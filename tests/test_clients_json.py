
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from globalsim.persistence.clients_json import load, save


class TestClientsJson(unittest.TestCase):

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = Path(self.temp.name) / "clients.json"

        self.clients = [
            {
                "id": 1,
                "nome": "João Silva",
                "email": "joao@email.com",
                "esim": "ESIM001",
                "pacote": 1,
                "status": "ativo"
            }
        ]

    def test_missing_file(self):
        self.assertEqual(load(self.path), [])

    def test_save_and_load(self):
        save(self.path, self.clients)

        self.assertEqual(load(self.path), self.clients)

    def test_create_directories(self):
        path = Path(self.temp.name) / "data" / "clients.json"

        save(path, self.clients)

        self.assertTrue(path.exists())
        self.assertEqual(load(path), self.clients)

    def test_utf8_encoding(self):
        save(self.path, self.clients)

        content = self.path.read_text(encoding="utf-8")

        self.assertIn("João Silva", content)

    def test_invalid_structure(self):
        self.path.write_text("{}", encoding="utf-8")

        with self.assertRaises(ValueError):
            load(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"), "{}"
        )

    def test_invalid_json(self):
        self.path.write_text("{invalid", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            load(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"), "{invalid"
        )

    def test_replace_failure(self):
        save(self.path, self.clients)

        original = self.path.read_bytes()

        with patch(
            "globalsim.persistence.clients_json.os.replace",
            side_effect=OSError("Falha simulada")
        ):
            with self.assertRaises(OSError):
                save(self.path, [])

        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(load(self.path), self.clients)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_serialization_failure(self):
        save(self.path, self.clients)

        original = self.path.read_bytes()

        with self.assertRaises(TypeError):
            save(self.path, [{"id": object()}])

        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(load(self.path), self.clients)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_overwrite_file(self):
        save(self.path, self.clients)

        updated = [dict(self.clients[0], status="inativo")]

        save(self.path, updated)

        self.assertEqual(load(self.path), updated)


if __name__ == "__main__":
    unittest.main()
