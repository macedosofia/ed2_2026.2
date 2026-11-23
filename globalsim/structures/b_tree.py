class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.records = []
        self.children = []


class BTree:
    def __init__(self, min_degree=3):
        if type(min_degree) is not int or min_degree < 2:
            raise ValueError("O grau mínimo deve ser um inteiro maior ou igual a 2.")

        self.min_degree = min_degree
        self.root = BTreeNode()

    def find(self, client_id):
        if type(client_id) is not int:
            raise ValueError("O ID do cliente deve ser um número inteiro.")

        return self._find_node(self.root, client_id)

    def _find_node(self, node, client_id):
        index = 0

        while index < len(node.keys) and client_id > node.keys[index]:
            index += 1

        if index < len(node.keys) and client_id == node.keys[index]:
            return node.records[index].copy()

        if node.leaf:
            return None

        return self._find_node(node.children[index], client_id)

    def _split_child(self, parent, index):
        t = self.min_degree

        child = parent.children[index]

        if len(child.keys) != 2 * t - 1:
            raise ValueError("O nó filho deve estar cheio para ser dividido.")

        if len(parent.keys) >= 2 * t - 1:
            raise ValueError("O nó pai não possui espaço para a mediana.")

        new_child = BTreeNode(leaf=child.leaf)

        median_key = child.keys[t - 1]
        median_record = child.records[t - 1]

        new_child.keys = child.keys[t:]
        new_child.records = child.records[t:]

        child.keys = child.keys[:t - 1]
        child.records = child.records[:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]

        parent.keys.insert(index, median_key)
        parent.records.insert(index, median_record)
        parent.children.insert(index + 1, new_child)

    def insert(self, record):
        if not isinstance(record, dict):
            raise ValueError("O cliente deve ser um dicionário.")

        client_id = record.get("id")

        if type(client_id) is not int:
            raise ValueError("O ID do cliente deve ser um número inteiro.")

        if self.find(client_id) is not None:
            raise ValueError("Já existe um cliente com esse ID.")

        if len(self.root.keys) == 2 * self.min_degree - 1:
            old_root = self.root

            new_root = BTreeNode(leaf=False)
            new_root.children.append(old_root)

            self._split_child(new_root, 0)

            self.root = new_root

        self._insert_non_full(self.root, record.copy())

    def _insert_non_full(self, node, record):
        client_id = record["id"]

        index = 0

        while index < len(node.keys) and client_id > node.keys[index]:
            index += 1

        if node.leaf:
            node.keys.insert(index, client_id)
            node.records.insert(index, record)
            return

        if len(node.children[index].keys) == 2 * self.min_degree - 1:
            self._split_child(node, index)

            if client_id > node.keys[index]:
                index += 1

        self._insert_non_full(node.children[index], record)

    def list_all(self):
        records = []

        self._collect_in_order(self.root, records)

        return records

    def _collect_in_order(self, node, records):
        for index, record in enumerate(node.records):

            if not node.leaf:
                self._collect_in_order(
                    node.children[index],
                    records
                )

            records.append(record.copy())

        if not node.leaf:
            self._collect_in_order(
                node.children[len(node.keys)],
                records
            )

    def update(self, client_id, record):
        if type(client_id) is not int:
            raise ValueError("O ID do cliente deve ser um número inteiro.")

        if not isinstance(record, dict):
            raise ValueError("O cliente deve ser um dicionário.")

        if type(record.get("id")) is not int or record["id"] != client_id:
            raise ValueError("O ID do cliente não pode ser alterado.")

        updated = self._update_node(self.root, client_id, record)

        if not updated:
            raise LookupError("Cliente não encontrado.")

    def _update_node(self, node, client_id, record):
        index = 0

        while index < len(node.keys) and client_id > node.keys[index]:
            index += 1

        if index < len(node.keys) and client_id == node.keys[index]:
            node.records[index] = record.copy()
            return True

        if node.leaf:
            return False

        return self._update_node(node.children[index], client_id, record)