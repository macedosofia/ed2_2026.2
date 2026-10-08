import unittest
from structures.hash_table import HashTable


class HashTableTests(unittest.TestCase):
    def test_collisions_update_and_removal(self):
        table = HashTable(1)
        for code in ['BR', 'PT', 'IT']:
            table.insert({'codigo': code, 'pais': code})
        self.assertEqual(table.statistics()['collisions'], 2)
        with self.assertRaises(ValueError):
            table.insert({'codigo': 'BR'})
        self.assertEqual(table.size, 3)
        table.update('PT', {'codigo': 'PT', 'pais': 'Portugal'})
        result = table.find('PT')
        result['pais'] = 'Mutated'
        self.assertEqual(table.find('PT')['pais'], 'Portugal')
        for code in ['PT', 'BR', 'IT']:
            table.remove(code)
            self.assertIsNone(table.find(code))
        self.assertEqual(table.list_all(), [])
        self.assertEqual(table.statistics()['load_factor'], 0)
        with self.assertRaises(LookupError):
            table.remove('ZZ')
