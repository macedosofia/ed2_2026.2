import unittest

from globalsim.structures.hash_table import HashTable


class HashTableTests(unittest.TestCase):

    def setUp(self):
        self.table = HashTable()

        self.brasil = {
            "codigo": "BR",
            "pais": "Brasil"
        }

    def test_insert_and_find(self):
        self.table.insert(self.brasil)

        result = self.table.find("BR")

        self.assertEqual(result, self.brasil)
        self.assertEqual(self.table.size, 1)

    def test_duplicate_country(self):
        self.table.insert(self.brasil)

        with self.assertRaises(ValueError):
            self.table.insert(self.brasil)

        self.assertEqual(self.table.size, 1)

    def test_update(self):
        self.table.insert(self.brasil)

        updated = {
            "codigo": "BR",
            "pais": "Brasil atualizado"
        }

        self.table.update("BR", updated)

        result = self.table.find("BR")

        self.assertEqual(
            result["pais"],
            "Brasil atualizado"
        )

    def test_remove(self):
        self.table.insert(self.brasil)

        self.table.remove("BR")

        result = self.table.find("BR")

        self.assertIsNone(result)
        self.assertEqual(self.table.size, 0)

    def test_statistics(self):
        self.table.insert(self.brasil)

        self.table.find("BR")
        self.table.find("PT")

        stats = self.table.statistics()

        self.assertEqual(stats["insertions"], 1)
        self.assertEqual(stats["lookups"], 2)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)

    def test_copy_protection(self):
        self.table.insert(self.brasil)

        self.brasil["pais"] = "Alterado externamente"

        result = self.table.find("BR")

        self.assertEqual(result["pais"], "Brasil")


if __name__ == "__main__":
    unittest.main()