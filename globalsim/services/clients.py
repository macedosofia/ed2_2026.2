from copy import deepcopy
from threading import RLock

from globalsim.models.client import normalize_id, validate_client
from globalsim.persistence import clients_json
from globalsim.structures.b_tree import BTree


class ClientService:

    def __init__(self, path):
        self.path = path
        self.tree = BTree()
        self.clients = []
        self.lock = RLock()

        for record in clients_json.load(self.path):
            client = validate_client(record)
            self._insert_record(client)

    def find(self, client_id):
        with self.lock:
            position = self.tree.find(normalize_id(client_id))

            if position is None:
                return None

            return self.clients[position].copy()

    def list_all(self):
        with self.lock:
            positions = self.tree.list_all()

            return [
                self.clients[position].copy()
                for position in positions
            ]

    def statistics(self):
        with self.lock:
            return self.tree.statistics()

    def _mutate(self, operation, *args):
        with self.lock:
            previous_tree = deepcopy(self.tree)
            previous_clients = deepcopy(self.clients)

            try:
                operation(*args)
                clients_json.save(self.path, self.clients)

            except Exception:
                self.tree = previous_tree
                self.clients = previous_clients
                raise

    def _insert_record(self, client):
        position = len(self.clients)

        self.tree.insert(client["id"], position)
        self.clients.append(client)

    def create(self, record):
        with self.lock:
            client = validate_client(record)
            self._mutate(self._insert_record, client)

    def _update_record(self, client_id, changes):
        position = self.tree.find(client_id)

        if position is None:
            raise LookupError("Cliente não encontrado.")

        current = self.clients[position]

        updated = dict(current)
        updated.update(changes)

        client = validate_client(updated)

        if client["id"] != client_id:
            raise ValueError("Não é permitido alterar o ID do cliente.")

        self.clients[position] = client

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
