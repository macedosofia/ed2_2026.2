
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

    def _update_record(self, client_id, changes):
        current = self.tree.find(client_id)

        if current is None:
            raise LookupError("Cliente não encontrado.")

        updated = dict(current)
        updated.update(changes)

        client = validate_client(updated)

        if client["id"] != client_id:
            raise ValueError("Não é permitido alterar o ID do cliente.")

        self.tree.update(client_id, client)

    def update(self, client_id, changes):
        with self.lock:
            client_id = normalize_id(client_id)

            if not isinstance(changes, dict):
                raise ValueError("As alterações devem ser um dicionário.")

            allowed_fields = {
                "id", "nome", "email", "esim", "pacote", "status"
            }

            if set(changes) - allowed_fields:
                raise ValueError("Campo de atualização inválido.")

            self._mutate(self._update_record, client_id, changes)
