import unittest

from globalsim.models.package import validate_package


class PackageModelTests(unittest.TestCase):

    def test_valid_package(self):
        package = {
            "codigo": 102,
            "nome": " Europa Plus ",
            "dados_gb": 10,
            "validade_dias": 30,
            "paises": ["pt", " FR ", "IT"],
        }

        result = validate_package(package)

        self.assertEqual(result["codigo"], 102)
        self.assertEqual(result["nome"], "Europa Plus")
        self.assertEqual(result["paises"], ["PT", "FR", "IT"])

        self.assertEqual(package["nome"], " Europa Plus ")

    def test_rejects_invalid_fields(self):
        valid_package = {
            "codigo": 102,
            "nome": "Europa Plus",
            "dados_gb": 10,
            "validade_dias": 30,
            "paises": ["PT", "FR"],
        }

        invalid_values = {
            "codigo": True,
            "nome": "   ",
            "dados_gb": 0,
            "validade_dias": -1,
            "paises": [],
        }

        for field, value in invalid_values.items():
            with self.subTest(field=field):
                package = valid_package.copy()
                package[field] = value

                with self.assertRaises(ValueError):
                    validate_package(package)

    def test_rejects_duplicate_countries(self):
        package = {
            "codigo": 102,
            "nome": "Europa Plus",
            "dados_gb": 10,
            "validade_dias": 30,
            "paises": ["PT", "pt"],
        }

        with self.assertRaises(ValueError):
            validate_package(package)


if __name__ == "__main__":
    unittest.main()