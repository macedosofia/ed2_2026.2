import unittest

from globalsim.structures.b_tree import BTreeNode


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