import unittest

from globalsim.structures.b_tree import BTree, BTreeNode


class BTreeNodeTests(unittest.TestCase):

    def test_new_node_is_empty_leaf(self):
        node = BTreeNode()

        self.assertTrue(node.leaf)
        self.assertEqual(node.keys, [])
        self.assertEqual(node.records, [])
        self.assertEqual(node.children, [])

    def test_internal_node(self):
        node = BTreeNode(leaf=False)

        self.assertFalse(node.leaf)

    def test_nodes_have_independent_lists(self):
        first = BTreeNode()
        second = BTreeNode()

        first.keys.append(10)

        self.assertEqual(first.keys, [10])
        self.assertEqual(second.keys, [])


if __name__ == "__main__":
    unittest.main()


class BTreeSearchTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree()

    def test_empty_tree(self):
        self.assertIsNone(self.tree.find(10))

    def test_find_key_in_root(self):
        self.tree.root.keys = [10, 30]
        self.tree.root.records = [
            {"id": 10, "nome": "Ana"},
            {"id": 30, "nome": "Maria"},
        ]

        result = self.tree.find(30)

        self.assertEqual(result["nome"], "Maria")
        self.assertIsNone(self.tree.find(20))

    def test_find_key_in_child(self):
        root = self.tree.root

        root.leaf = False
        root.keys = [30, 60]
        root.records = [
            {"id": 30},
            {"id": 60},
        ]

        left = BTreeNode()
        left.keys = [10, 20]
        left.records = [
            {"id": 10},
            {"id": 20},
        ]

        middle = BTreeNode()
        middle.keys = [40, 50]
        middle.records = [
            {"id": 40},
            {"id": 50},
        ]

        right = BTreeNode()
        right.keys = [70, 80]
        right.records = [
            {"id": 70},
            {"id": 80},
        ]

        root.children = [left, middle, right]

        self.assertEqual(self.tree.find(50)["id"], 50)
        self.assertEqual(self.tree.find(70)["id"], 70)
        self.assertEqual(self.tree.find(30)["id"], 30)
        self.assertIsNone(self.tree.find(35))

    def test_find_returns_copy(self):
        self.tree.root.keys = [10]
        self.tree.root.records = [
            {"id": 10, "nome": "Ana"},
        ]

        result = self.tree.find(10)
        result["nome"] = "Alterado"

        self.assertEqual(self.tree.find(10)["nome"], "Ana")

    def test_rejects_invalid_minimum_degree(self):
        with self.assertRaises(ValueError):
            BTree(min_degree=1)


class BTreeSplitTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(min_degree=3)

    def test_split_full_leaf(self):
        parent = BTreeNode(leaf=False)
        child = BTreeNode()

        child.keys = [10, 20, 30, 40, 50]
        child.records = [
            {"id": key} for key in child.keys
        ]

        parent.children = [child]

        self.tree._split_child(parent, 0)

        self.assertEqual(parent.keys, [30])
        self.assertEqual(parent.records, [{"id": 30}])

        self.assertEqual(parent.children[0].keys, [10, 20])
        self.assertEqual(parent.children[1].keys, [40, 50])

        self.assertEqual(len(parent.children), 2)

        self.assertTrue(parent.children[0].leaf)
        self.assertTrue(parent.children[1].leaf)

        self.tree.root = parent

        for key in [10, 20, 30, 40, 50]:
            self.assertEqual(self.tree.find(key), {"id": key})

    def test_split_full_internal_node(self):
        parent = BTreeNode(leaf=False)
        child = BTreeNode(leaf=False)

        child.keys = [10, 20, 30, 40, 50]
        child.records = [
            {"id": key} for key in child.keys
        ]

        child.children = []

        for key in [5, 15, 25, 35, 45, 55]:
            leaf = BTreeNode()
            leaf.keys = [key]
            leaf.records = [{"id": key}]
            child.children.append(leaf)

        parent.children = [child]

        self.tree._split_child(parent, 0)

        left = parent.children[0]
        right = parent.children[1]

        self.assertEqual(parent.keys, [30])

        self.assertEqual(left.keys, [10, 20])
        self.assertEqual(right.keys, [40, 50])

        self.assertFalse(left.leaf)
        self.assertFalse(right.leaf)

        self.assertEqual(len(left.children), 3)
        self.assertEqual(len(right.children), 3)

        self.assertEqual(
            [node.keys[0] for node in left.children],
            [5, 15, 25]
        )

        self.assertEqual(
            [node.keys[0] for node in right.children],
            [35, 45, 55]
        )

        self.tree.root = parent

        for key in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
            self.assertEqual(self.tree.find(key), {"id": key})


class BTreeInsertionTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(min_degree=3)

    def test_insert_first_client(self):
        self.tree.insert({"id": 10, "nome": "Ana"})

        self.assertEqual(
            self.tree.find(10),
            {"id": 10, "nome": "Ana"}
        )

    def test_insert_multiple_clients(self):
        ids = [30, 10, 50, 20, 40]

        for client_id in ids:
            self.tree.insert({"id": client_id})

        self.assertEqual(
            self.tree.root.keys,
            [10, 20, 30, 40, 50]
        )

        for client_id in ids:
            self.assertEqual(
                self.tree.find(client_id),
                {"id": client_id}
            )

    def test_insert_causes_root_split(self):
        ids = [10, 20, 30, 40, 50, 60]

        for client_id in ids:
            self.tree.insert({"id": client_id})

        self.assertEqual(self.tree.root.keys, [30])
        self.assertFalse(self.tree.root.leaf)

        self.assertEqual(
            self.tree.root.children[0].keys,
            [10, 20]
        )

        self.assertEqual(
            self.tree.root.children[1].keys,
            [40, 50, 60]
        )

    def test_duplicate_id(self):
        self.tree.insert({"id": 10})

        with self.assertRaises(ValueError):
            self.tree.insert({"id": 10})

    def test_many_insertions(self):
        for client_id in range(1, 101):
            self.tree.insert({"id": client_id})

        for client_id in range(1, 101):
            self.assertEqual(
                self.tree.find(client_id),
                {"id": client_id}
            )

        self.assertIsNone(self.tree.find(101))

    def test_insert_copies_record(self):
        record = {"id": 10, "nome": "Ana"}

        self.tree.insert(record)
        record["nome"] = "Alterado"

        self.assertEqual(
            self.tree.find(10)["nome"],
            "Ana"
        )

    def test_rejects_invalid_record(self):
        with self.assertRaises(ValueError):
            self.tree.insert(None)

        with self.assertRaises(ValueError):
            self.tree.insert({"id": "10"})


class BTreeInvariantTests(unittest.TestCase):

    def assert_valid_tree(self, tree):
        t = tree.min_degree
        leaf_depths = set()

        def check_node(node, minimum, maximum, depth, is_root=False):
            key_count = len(node.keys)

            self.assertEqual(key_count, len(node.records))

            self.assertLessEqual(key_count, 2 * t - 1)

            if not is_root:
                self.assertGreaterEqual(key_count, t - 1)
            elif not node.leaf:
                self.assertGreaterEqual(key_count, 1)

            self.assertEqual(node.keys, sorted(node.keys))

            for index, key in enumerate(node.keys):

                self.assertEqual(node.records[index]["id"], key)

                if minimum is not None:
                    self.assertGreater(key, minimum)

                if maximum is not None:
                    self.assertLess(key, maximum)

                if index > 0:
                    self.assertGreater(key, node.keys[index - 1])

            if node.leaf:
                self.assertEqual(node.children, [])
                leaf_depths.add(depth)
                return key_count

            self.assertEqual(len(node.children), key_count + 1)

            total = key_count

            boundaries = [minimum] + node.keys + [maximum]

            for index, child in enumerate(node.children):
                total += check_node(
                    child,
                    boundaries[index],
                    boundaries[index + 1],
                    depth + 1
                )

            return total

        total = check_node(
            tree.root,
            None,
            None,
            0,
            is_root=True
        )

        self.assertEqual(len(leaf_depths), 1)

        return total

    def test_preserves_invariants_with_1000_clients(self):
        import random

        for degree in [2, 3, 4]:
            for order in ["ascending", "descending", "random"]:

                with self.subTest(degree=degree, order=order):
                    tree = BTree(min_degree=degree)

                    ids = list(range(1, 1001))

                    if order == "descending":
                        ids.reverse()

                    elif order == "random":
                        random.Random(2026).shuffle(ids)

                    for client_id in ids:
                        tree.insert({"id": client_id})

                    total = self.assert_valid_tree(tree)

                    self.assertEqual(total, 1000)

                    for client_id in range(1, 1001):
                        self.assertEqual(
                            tree.find(client_id),
                            {"id": client_id}
                        )

                    self.assertIsNone(tree.find(1001))

    def test_preserves_invariants_after_every_insertion(self):
        import random

        tree = BTree(min_degree=3)

        ids = list(range(1, 121))
        random.Random(42).shuffle(ids)

        for expected_total, client_id in enumerate(ids, start=1):
            tree.insert({"id": client_id})

            total = self.assert_valid_tree(tree)

            self.assertEqual(total, expected_total)    