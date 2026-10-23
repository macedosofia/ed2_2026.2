import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from globalsim.services.countries import CountryService


class CountryServiceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'countries.json'
        self.record = dict(codigo='IT', pais='Itália', regiao='Europa',
                           operadora='Operadora IT', tecnologia='5G')

    def test_loads_records_into_dict_and_tracks_initial_load(self):
        records = [self.record, dict(self.record, codigo='DE', pais='Alemanha')]
        self.path.write_text(json.dumps(records), encoding='utf-8')
        service = CountryService(self.path)
        stats = service.statistics()
        self.assertEqual(stats['size'], 2)
        self.assertEqual(stats["loaded_records"], stats["size"])
        self.assertEqual(stats["insertions"], 0)
        self.assertEqual(stats["lookups"], 0)
        with patch('globalsim.services.countries.countries_json.load', side_effect=AssertionError('file read')):
            self.assertEqual(service.find(' it '), self.record)
            self.assertEqual([record['codigo'] for record in service.list_all()], ['DE', 'IT'])

    def test_startup_rejects_invalid_or_duplicate_records_without_overwriting_file(self):
        cases = [[dict(self.record, tecnologia='')],
                 [self.record, dict(self.record, codigo=' it ')]]
        for records in cases:
            with self.subTest(records=records):
                self.path.write_text(json.dumps(records), encoding='utf-8')
                previous = self.path.read_bytes()
                with self.assertRaises(ValueError):
                    CountryService(self.path)
                self.assertEqual(self.path.read_bytes(), previous)

    def test_create_update_and_removal_survive_restart(self):
        service = CountryService(self.path)
        service.create(self.record)
        self.assertEqual(CountryService(self.path).find('IT'), self.record)
        updated = dict(self.record, operadora='Nova operadora')
        service.update('it', updated)
        restarted = CountryService(self.path)
        self.assertEqual(restarted.find('IT'), updated)
        restarted.remove('it')
        self.assertEqual(CountryService(self.path).list_all(), [])

    def test_failed_mutations_restore_records_file_and_all_metrics(self):
        service = CountryService(self.path)
        service.create(self.record)
        before_records = service.list_all()
        before_stats = service.statistics()
        before_file = self.path.read_bytes()
        operations = [
            (service.create, (dict(self.record, codigo='DE'),)),
            (service.update, ('IT', dict(self.record, pais='Changed'))),
            (service.remove, ('IT',)),
        ]
        with patch('globalsim.services.countries.countries_json.save', side_effect=OSError('disk error')):
            for operation, args in operations:
                with self.subTest(operation=operation.__name__):
                    with self.assertRaises(OSError):
                        operation(*args)
                    self.assertEqual(service.list_all(), before_records)
                    self.assertEqual(service.statistics(), before_stats)
                    self.assertEqual(self.path.read_bytes(), before_file)

    def test_copies_protect_records_and_normalized_duplicates_are_rejected(self):
        service = CountryService(self.path)
        service.create(self.record)
        service.find('IT')['pais'] = 'Changed'
        service.list_all()[0]['pais'] = 'Changed'
        self.assertEqual(service.find('IT'), self.record)
        before_file = self.path.read_bytes()
        with self.assertRaises(ValueError):
            service.create(dict(self.record, codigo=' it '))
        self.assertEqual(service.list_all(), [self.record])
        self.assertEqual(self.path.read_bytes(), before_file)
