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