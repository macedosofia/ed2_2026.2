import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app


class CountryRoutesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'countries.json'
        self.config = {'TESTING': True, 'SECRET_KEY': 'test', 'COUNTRIES_PATH': self.path}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.record = dict(codigo='BR', pais='Brasil', regiao='América', operadora='Teste', tecnologia='5G')

    def test_full_lifecycle_and_restart(self):
        for url in ['/', '/countries', '/countries/new', '/coverage', '/instrumentation']:
            self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post('/countries/new', data=self.record)
        self.assertEqual(response.status_code, 303)
        self.assertIn('Brasil', self.client.get('/coverage?codigo=br').text)
        self.assertEqual(self.client.post('/countries/new', data=self.record).status_code, 400)
        updated = dict(self.record, operadora='Nova operadora')
        self.assertEqual(self.client.post('/countries/BR/edit', data=updated).status_code, 303)
        restarted = create_app(self.config).test_client()
        self.assertIn('Nova operadora', restarted.get('/countries').text)
        self.assertEqual(self.client.get('/countries/BR/delete').status_code, 405)
        self.assertIsNotNone(self.app.extensions['countries'].find('BR'))
        self.assertEqual(self.client.post('/countries/BR/delete').status_code, 303)
        self.assertEqual(json.loads(self.path.read_text()), [])
        self.assertIn('Cobertura indisponível', self.client.get('/coverage?codigo=BR').text)

    def test_invalid_missing_and_immutable_codes(self):
        self.assertEqual(self.client.post('/countries/new', data={}).status_code, 400)
        self.assertEqual(self.client.get('/coverage?codigo=123').status_code, 400)
        self.assertEqual(self.client.get('/countries/ZZ/edit').status_code, 404)
        self.assertEqual(self.client.post('/countries/ZZ/edit', data=self.record).status_code, 404)
        self.assertEqual(self.client.post('/countries/ZZ/delete').status_code, 404)
        self.client.post('/countries/new', data=dict(self.record, codigo=' br '))
        self.assertEqual(self.client.post('/countries/BR/edit', data=dict(self.record, codigo='PT')).status_code, 400)
        self.assertIsNotNone(self.app.extensions['countries'].find('BR'))
        self.assertIsNone(self.app.extensions['countries'].find('PT'))

    def test_write_failure_preserves_memory_and_file(self):
        self.client.post('/countries/new', data=self.record)
        previous = self.path.read_bytes()
        service = self.app.extensions['countries']
        before = service.table.statistics()
        with patch('services.countries.countries_json.save', side_effect=OSError('disk error')):
            for url, data in [('/countries/new', dict(self.record, codigo='PT')), ('/countries/BR/edit', dict(self.record, pais='Changed')), ('/countries/BR/delete', {})]:
                self.assertEqual(self.client.post(url, data=data).status_code, 503)
                self.assertEqual(service.list_all(), [self.record])
                self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(service.statistics()['collisions'], before['collisions'])

    def test_queries_use_hash_without_reading_json(self):
        self.client.post('/countries/new', data=self.record)
        with patch('services.countries.countries_json.load', side_effect=AssertionError('unexpected file read')):
            with patch.object(self.app.extensions['countries'].table, 'find', wraps=self.app.extensions['countries'].table.find) as find:
                self.assertIn('Brasil', self.client.get('/coverage?codigo=BR').text)
                find.assert_called_once_with('BR')
            self.assertIn('Brasil', self.client.get('/countries').text)

    def test_corrupt_json_is_not_overwritten(self):
        self.path.write_text('{broken')
        with self.assertRaises(ValueError):
            create_app(self.config)
        self.assertEqual(self.path.read_text(), '{broken')
