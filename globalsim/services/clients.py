
from copy import deepcopy
from threading import RLock

from globalsim.models.client import normalize_id, validate_client
from globalsim.persistence import clients_json
from globalsim.structures.b_tree import BTree


class ClientService:

    def __init__(self, path):
        self.path = path
        self.tree = BTree()
        self.lock = RLock()

        for record in clients_json.load(self.path):
            client = validate_client(record)
            self.tree.insert(client)

    def find(self, client_id):
        with self.lock:
            return self.tree.find(normalize_id(client_id))

    def list_all(self):
        with self.lock:
            return self.tree.list_all()

    def statistics(self):
        with self.lock:
            return self.tree.statistics()

    def _mutate(self, operation, *args):
        with self.lock:
            previous = deepcopy(self.tree)

            try:
                operation(*args)
                clients_json.save(self.path, self.tree.list_all())

            except Exception:
                self.tree = previous
                raise

    def create(self, record):
        with self.lock:
            client = validate_client(record)
            self._mutate(self.tree.insert, client)
