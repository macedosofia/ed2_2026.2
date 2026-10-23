import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from globalsim.persistence import countries_json


class CountryPersistenceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.path = self.directory / 'countries.json'
        self.records = [dict(codigo='JP', pais='Japão', regiao='Ásia',
                             operadora='Operadora JP', tecnologia='5G')]

    def test_missing_file_is_empty_without_creating_it(self):
        self.assertEqual(countries_json.load(self.path), [])
        self.assertFalse(self.path.exists())

    def test_round_trip_preserves_unicode_and_creates_directory(self):
        path = self.directory / 'nested' / 'countries.json'
        countries_json.save(path, self.records)
        self.assertEqual(countries_json.load(path), self.records)
        self.assertIn('Japão', path.read_text(encoding='utf-8'))
        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_invalid_documents_are_not_overwritten(self):
        for contents in ['{broken', '{}', 'null', '"Brasil"']:
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding='utf-8')
                with self.assertRaises(ValueError):
                    countries_json.load(self.path)
                self.assertEqual(self.path.read_text(encoding='utf-8'), contents)

    def test_failed_replacement_preserves_original_and_cleans_temporary_file(self):
        countries_json.save(self.path, self.records)
        previous = self.path.read_bytes()
        with patch('globalsim.persistence.countries_json.os.replace', side_effect=OSError('disk error')):
            with self.assertRaises(OSError):
                countries_json.save(self.path, [])
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_failed_serialization_preserves_original_and_cleans_temporary_file(self):
        countries_json.save(self.path, self.records)
        previous = self.path.read_bytes()
        with self.assertRaises(TypeError):
            countries_json.save(self.path, [dict(codigo=object())])
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(self.directory.iterdir()), [self.path])
