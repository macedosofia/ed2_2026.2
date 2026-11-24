import json
import tempfile
import unittest
from pathlib import Path

from globalsim.services.packages import PackageService


class PackageServiceTests(unittest.TestCase):

    def test_loads_catalog_and_finds_packages(self):
        service = PackageService()

        packages = service.list_all()

        self.assertEqual(len(packages), 5)

        self.assertEqual(
            [package["codigo"] for package in packages],
            [101, 102, 201, 202, 301]
        )

        self.assertEqual(
            service.find(102)["nome"],
            "Europa Plus"
        )

        self.assertIsNone(service.find(999))

    def test_queries_return_independent_copies(self):
        service = PackageService()

        package = service.find(102)

        package["nome"] = "Alterado"
        package["paises"].append("JP")

        original = service.find(102)

        self.assertEqual(original["nome"], "Europa Plus")
        self.assertNotIn("JP", original["paises"])

        packages = service.list_all()
        packages[0]["paises"].clear()

        self.assertEqual(
            service.find(101)["paises"],
            ["PT", "ES", "FR", "IT"]
        )

    def test_rejects_invalid_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packages.json"

            with self.assertRaises(FileNotFoundError):
                PackageService(path)

            path.write_text("{}", encoding="utf-8")

            with self.assertRaises(ValueError):
                PackageService(path)

            path.write_text("{", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                PackageService(path)

            package = PackageService().find(101)

            path.write_text(
                json.dumps([package, package]),
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                PackageService(path)


if __name__ == "__main__":
    unittest.main()