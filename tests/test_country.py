import unittest

from globalsim.models.country import FIELDS, normalize_code, validate_country


class CountryModelTests(unittest.TestCase):
    def setUp(self):
        self.record = dict(codigo='BR', pais='Brasil', regiao='América do Sul',
                           operadora='Operadora BR', tecnologia='5G')

    def test_normalizes_country_without_mutating_input(self):
        record = {field: f' {value} ' for field, value in self.record.items()}
        record['codigo'] = ' br '
        original = record.copy()
        self.assertEqual(validate_country(record), self.record)
        self.assertEqual(record, original)

    def test_rejects_invalid_codes(self):
        for code in [None, 12, '', ' ', 'B', 'BRA', 'B1', 'B R', 'ÇR']:
            with self.subTest(code=code), self.assertRaises(ValueError):
                normalize_code(code)

    def test_requires_every_field_to_be_nonempty_text(self):
        for field in FIELDS:
            for value in [None, '', ' \t ', 0, []]:
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    validate_country(dict(self.record, **{field: value}))
            missing = self.record.copy()
            del missing[field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                validate_country(missing)

    def test_rejects_non_mapping_records(self):
        for record in [None, [], 'Brasil', 7]:
            with self.subTest(record=record), self.assertRaises(ValueError):
                validate_country(record)
