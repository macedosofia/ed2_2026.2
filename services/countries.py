from copy import deepcopy
from threading import RLock
from models.country import normalize_code, validate_country
from persistence import countries_json
from structures.hash_table import HashTable


class CountryService:
    def __init__(self, path):
        self.path = path
        self.table = HashTable()
        self.lock = RLock()
        for record in countries_json.load(path):
            self.table.insert(validate_country(record))
        self.table.load_collisions = self.table.collisions

    def find(self, code):
        with self.lock:
            return self.table.find(normalize_code(code))

    def list_all(self):
        with self.lock:
            return sorted(self.table.list_all(), key=lambda item: item["codigo"])

    def statistics(self):
        with self.lock:
            return self.table.statistics()

    def _mutate(self, operation, *args):
        with self.lock:
            previous = deepcopy(self.table)
            try:
                operation(*args)
                countries_json.save(self.path, self.table.list_all())
            except Exception:
                self.table = previous
                raise

    def create(self, record):
        with self.lock:
            self._mutate(self.table.insert, validate_country(record))

    def update(self, code, record):
        with self.lock:
            self._mutate(self.table.update, normalize_code(code), validate_country(record))

    def remove(self, code):
        with self.lock:
            self._mutate(self.table.remove, normalize_code(code))
