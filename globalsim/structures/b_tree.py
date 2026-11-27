class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.positions = []
        self.children = []


class BTree:
    def __init__(self, min_degree=3):
        if type(min_degree) is not int or min_degree < 2:
            raise ValueError("O grau mínimo deve ser um inteiro maior ou igual a 2.")

        self.min_degree = min_degree
        self.root = BTreeNode()

        self._size = 0
        self._splits = 0
        self._lookups = 0


    def find(self, client_id):
        if type(client_id) is not int:
            raise ValueError("O ID do cliente deve ser um número inteiro.")

        self._lookups += 1

        return self._find_node(self.root, client_id)

    def _find_node(self, node, client_id):
        index = 0

        while index < len(node.keys) and client_id > node.keys[index]:
            index += 1

        if index < len(node.keys) and client_id == node.keys[index]:
            return node.positions[index]

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
        median_position = child.positions[t - 1]

        new_child.keys = child.keys[t:]
        new_child.positions = child.positions[t:]

        child.keys = child.keys[:t - 1]
        child.positions = child.positions[:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]

        parent.keys.insert(index, median_key)
        parent.positions.insert(index, median_position)
        parent.children.insert(index + 1, new_child)

        self._splits += 1


    def insert(self, client_id, position):
        if type(client_id) is not int:
            raise ValueError("O ID do cliente deve ser um número inteiro.")

        if type(position) is not int or position < 0:
            raise ValueError("A posição deve ser um inteiro não negativo.")

        if self._find_node(self.root, client_id) is not None:
            raise ValueError("Já existe um cliente com esse ID.")

        if len(self.root.keys) == 2 * self.min_degree - 1:
            old_root = self.root

            new_root = BTreeNode(leaf=False)
            new_root.children.append(old_root)

            self._split_child(new_root, 0)

            self.root = new_root

        self._insert_non_full(self.root, client_id, position)

        self._size += 1

    def _insert_non_full(self, node, client_id, position):
        index = 0

        while index < len(node.keys) and client_id > node.keys[index]:
            index += 1

        if node.leaf:
            node.keys.insert(index, client_id)
            node.positions.insert(index, position)
            return

        if len(node.children[index].keys) == 2 * self.min_degree - 1:
            self._split_child(node, index)

            if client_id > node.keys[index]:
                index += 1

        self._insert_non_full(
            node.children[index],
            client_id,
            position
        )


    def list_all(self):
        positions = []

        self._collect_in_order(self.root, positions)

        return positions

    def _collect_in_order(self, node, positions):
        for index, position in enumerate(node.positions):

            if not node.leaf:
                self._collect_in_order(
                    node.children[index],
                    positions
                )

            positions.append(position)

        if not node.leaf:
            self._collect_in_order(
                node.children[len(node.keys)],
                positions
            )


    def _height(self):
        if self._size == 0:
            return 0

        height = 1
        node = self.root

        while not node.leaf:
            height += 1
            node = node.children[0]

        return height

    def _count_nodes(self, node):
        count = 1

        for child in node.children:
            count += self._count_nodes(child)

        return count

    def statistics(self):
        return {
            "size": self._size,
            "height": self._height(),
            "node_count": (
                0 if self._size == 0
                else self._count_nodes(self.root)
            ),
            "splits": self._splits,
            "lookups": self._lookups,
        }
