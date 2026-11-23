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