import tempfile
import unittest
from pathlib import Path

from app import create_app


class DemoTests(unittest.TestCase):
    def test_demo_coverage_collision_metrics_and_restart(self):
        demo_path = Path(__file__).resolve().parents[1] / 'data' / 'countries.demo.json'
        original_demo = demo_path.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'countries.json'
            path.write_bytes(original_demo)
            config = {'TESTING': True, 'SECRET_KEY': 'test', 'COUNTRIES_PATH': path}
            app = create_app(config)
            client = app.test_client()
            service = app.extensions['countries']
            self.assertEqual({item['codigo'] for item in service.list_all()},
                             {'BR', 'PT', 'ES', 'FR', 'IT', 'US', 'CA', 'JP'})
            for code in ['BR', 'PT', 'ES', 'FR', 'IT', 'US', 'CA', 'JP']:
                with self.subTest(code=code):
                    response = client.get('/coverage', query_string={'codigo': code})
                    self.assertEqual(response.status_code, 200)
                    self.assertIn('Cobertura disponível', response.text)
            self.assertIn('Cobertura indisponível', client.get('/coverage?codigo=DE').text)
            before = service.statistics()
            germany = dict(codigo='DE', pais='Alemanha', regiao='Europa',
                           operadora='Operadora DE', tecnologia='5G')
            self.assertEqual(client.post('/countries/new', data=germany).status_code, 303)
            after = service.statistics()
            self.assertEqual(after['occupancy'][1], before['occupancy'][1] + 1)
            self.assertEqual(after['collisions'], before['collisions'] + 1)
            page = client.get('/instrumentation')
            self.assertEqual(page.status_code, 200)
            self.assertIn('<dt>Países</dt><dd>9</dd>', page.text)
            self.assertIn('<dt>Colisões nas inserções posteriores</dt><dd>1</dd>', page.text)
            self.assertEqual(client.post('/countries/DE/delete').status_code, 303)
            restarted = create_app(config)
            self.assertEqual(restarted.extensions['countries'].statistics()['size'], 8)
            restarted_client = restarted.test_client()
            self.assertIn('Itália', restarted_client.get('/coverage?codigo=IT').text)
            self.assertIn('Cobertura indisponível', restarted_client.get('/coverage?codigo=DE').text)
        self.assertEqual(demo_path.read_bytes(), original_demo)
