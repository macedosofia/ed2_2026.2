
import unittest

from globalsim.models.client import validate_client


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = {
            "id": 1,
            "nome": "Maria Silva",
            "email": "maria@email.com",
            "esim": "ESIM001",
            "pacote": 1,
            "status": "ativo"
        }

    def test_valid_client(self):
        self.assertEqual(validate_client(self.client), self.client)

    def test_normalize_name(self):
        self.client["nome"] = "  Maria Silva  "
        result = validate_client(self.client)

        self.assertEqual(result["nome"], "Maria Silva")

    def test_invalid_id(self):
        for value in [-1, 0, "1", 1.5, True, None]:
            with self.subTest(value=value):
                self.client["id"] = value

                with self.assertRaises(ValueError):
                    validate_client(self.client)

    def test_invalid_email(self):
        self.client["email"] = "emailinvalido"

        with self.assertRaises(ValueError):
            validate_client(self.client)

    def test_empty_name(self):
        self.client["nome"] = "   "

        with self.assertRaises(ValueError):
            validate_client(self.client)

    def test_optional_fields(self):
        self.client["esim"] = None
        self.client["pacote"] = None

        result = validate_client(self.client)

        self.assertIsNone(result["esim"])
        self.assertIsNone(result["pacote"])

    def test_invalid_package(self):
        for value in [-1, 0, "1", 1.5, True]:
            with self.subTest(value=value):
                self.client["pacote"] = value

                with self.assertRaises(ValueError):
                    validate_client(self.client)

    def test_invalid_esim(self):
        self.client["esim"] = ""

        with self.assertRaises(ValueError):
            validate_client(self.client)

    def test_invalid_status(self):
        self.client["status"] = ""

        with self.assertRaises(ValueError):
            validate_client(self.client)

    def test_invalid_record(self):
        with self.assertRaises(ValueError):
            validate_client("cliente")

    def test_independent_record(self):
        result = validate_client(self.client)
        result["nome"] = "Outro nome"

        self.assertEqual(self.client["nome"], "Maria Silva")


if __name__ == "__main__":
    unittest.main()
