import random
import unittest

from globalsim.structures.b_tree import BTree, BTreeNode


class BTreeNodeTests(unittest.TestCase):

    def test_new_node_is_empty_leaf(self):
        node = BTreeNode()

        self.assertTrue(node.leaf)
        self.assertEqual(node.keys, [])
        self.assertEqual(node.positions, [])
        self.assertEqual(node.children, [])

    def test_internal_node(self):
        node = BTreeNode(leaf=False)

        self.assertFalse(node.leaf)

    def test_nodes_have_independent_lists(self):
        first = BTreeNode()
        second = BTreeNode()

        first.keys.append(10)
        first.positions.append(0)
        first.children.append(BTreeNode())

        self.assertEqual(first.keys, [10])
        self.assertEqual(first.positions, [0])
        self.assertEqual(len(first.children), 1)

        self.assertEqual(second.keys, [])
        self.assertEqual(second.positions, [])
        self.assertEqual(second.children, [])


class BTreeSearchTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree()

    def test_empty_tree(self):
        self.assertIsNone(self.tree.find(10))

    def test_find_key_in_root(self):
        self.tree.root.keys = [10, 30]
        self.tree.root.positions = [1, 0]

        self.assertEqual(self.tree.find(10), 1)
        self.assertEqual(self.tree.find(30), 0)
        self.assertIsNone(self.tree.find(20))

    def test_find_key_in_child(self):
        root = self.tree.root

        root.leaf = False
        root.keys = [30, 60]
        root.positions = [4, 7]

        left = BTreeNode()
        left.keys = [10, 20]
        left.positions = [2, 0]

        middle = BTreeNode()
        middle.keys = [40, 50]
        middle.positions = [6, 1]

        right = BTreeNode()
        right.keys = [70, 80]
        right.positions = [3, 5]

        root.children = [left, middle, right]

        self.assertEqual(self.tree.find(10), 2)
        self.assertEqual(self.tree.find(20), 0)
        self.assertEqual(self.tree.find(30), 4)
        self.assertEqual(self.tree.find(40), 6)
        self.assertEqual(self.tree.find(50), 1)
        self.assertEqual(self.tree.find(60), 7)
        self.assertEqual(self.tree.find(70), 3)
        self.assertEqual(self.tree.find(80), 5)

        self.assertIsNone(self.tree.find(35))

    def test_find_returns_integer_position(self):
        self.tree.insert(10, 3)

        result = self.tree.find(10)

        self.assertIs(type(result), int)
        self.assertEqual(result, 3)

    def test_find_position_zero(self):
        self.tree.insert(10, 0)

        self.assertEqual(self.tree.find(10), 0)
        self.assertIsNotNone(self.tree.find(10))
        self.assertIsNone(self.tree.find(99))

    def test_find_rejects_invalid_id(self):
        for client_id in [None, "10", True, 10.5, {}]:
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    self.tree.find(client_id)

    def test_rejects_invalid_minimum_degree(self):
        for degree in [1, 0, -1, True, "3", 2.5, None]:
            with self.subTest(degree=degree):
                with self.assertRaises(ValueError):
                    BTree(min_degree=degree)


class BTreeSplitTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(min_degree=3)

    def test_split_full_leaf(self):
        parent = BTreeNode(leaf=False)
        child = BTreeNode()

        child.keys = [10, 20, 30, 40, 50]
        child.positions = [3, 0, 4, 1, 2]

        expected = dict(zip(child.keys, child.positions))

        parent.children = [child]

        self.tree._split_child(parent, 0)

        self.assertEqual(parent.keys, [30])
        self.assertEqual(parent.positions, [4])

        self.assertEqual(parent.children[0].keys, [10, 20])
        self.assertEqual(parent.children[0].positions, [3, 0])

        self.assertEqual(parent.children[1].keys, [40, 50])
        self.assertEqual(parent.children[1].positions, [1, 2])

        self.assertEqual(len(parent.children), 2)

        self.assertTrue(parent.children[0].leaf)
        self.assertTrue(parent.children[1].leaf)

        self.tree.root = parent

        for key, position in expected.items():
            self.assertEqual(self.tree.find(key), position)

    def test_split_full_internal_node(self):
        parent = BTreeNode(leaf=False)
        child = BTreeNode(leaf=False)

        child.keys = [10, 20, 30, 40, 50]
        child.positions = [8, 0, 10, 2, 6]

        expected = dict(zip(child.keys, child.positions))

        child.children = []

        leaf_keys = [5, 15, 25, 35, 45, 55]
        leaf_positions = [1, 3, 4, 5, 7, 9]

        for key, position in zip(leaf_keys, leaf_positions):
            leaf = BTreeNode()
            leaf.keys = [key]
            leaf.positions = [position]

            child.children.append(leaf)
            expected[key] = position

        parent.children = [child]

        self.tree._split_child(parent, 0)

        left = parent.children[0]
        right = parent.children[1]

        self.assertEqual(parent.keys, [30])
        self.assertEqual(parent.positions, [10])

        self.assertEqual(left.keys, [10, 20])
        self.assertEqual(left.positions, [8, 0])

        self.assertEqual(right.keys, [40, 50])
        self.assertEqual(right.positions, [2, 6])

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

        for key, position in expected.items():
            self.assertEqual(self.tree.find(key), position)

    def test_rejects_split_of_non_full_child(self):
        parent = BTreeNode(leaf=False)
        child = BTreeNode()

        child.keys = [10, 20]
        child.positions = [1, 0]

        parent.children = [child]

        with self.assertRaises(ValueError):
            self.tree._split_child(parent, 0)

    def test_rejects_split_when_parent_is_full(self):
        parent = BTreeNode(leaf=False)
        parent.keys = [60, 70, 80, 90, 100]
        parent.positions = [5, 6, 7, 8, 9]

        child = BTreeNode()
        child.keys = [10, 20, 30, 40, 50]
        child.positions = [0, 1, 2, 3, 4]

        parent.children = [child]

        with self.assertRaises(ValueError):
            self.tree._split_child(parent, 0)


class BTreeInsertionTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(min_degree=3)

    def test_insert_first_client(self):
        self.tree.insert(10, 0)

        self.assertEqual(self.tree.root.keys, [10])
        self.assertEqual(self.tree.root.positions, [0])
        self.assertEqual(self.tree.find(10), 0)

    def test_insert_multiple_clients(self):
        ids = [30, 10, 50, 20, 40]

        for position, client_id in enumerate(ids):
            self.tree.insert(client_id, position)

        self.assertEqual(
            self.tree.root.keys,
            [10, 20, 30, 40, 50]
        )

        self.assertEqual(
            self.tree.root.positions,
            [1, 3, 0, 4, 2]
        )

        for position, client_id in enumerate(ids):
            self.assertEqual(
                self.tree.find(client_id),
                position
            )

    def test_insert_causes_root_split(self):
        ids = [30, 10, 20, 50, 40, 60]

        for position, client_id in enumerate(ids):
            self.tree.insert(client_id, position)

        self.assertEqual(self.tree.root.keys, [30])
        self.assertEqual(self.tree.root.positions, [0])

        self.assertFalse(self.tree.root.leaf)

        self.assertEqual(
            self.tree.root.children[0].keys,
            [10, 20]
        )

        self.assertEqual(
            self.tree.root.children[0].positions,
            [1, 2]
        )

        self.assertEqual(
            self.tree.root.children[1].keys,
            [40, 50, 60]
        )

        self.assertEqual(
            self.tree.root.children[1].positions,
            [4, 3, 5]
        )

        for position, client_id in enumerate(ids):
            self.assertEqual(
                self.tree.find(client_id),
                position
            )

    def test_duplicate_id(self):
        self.tree.insert(10, 0)

        original = self.tree.statistics()

        with self.assertRaises(ValueError):
            self.tree.insert(10, 5)

        self.assertEqual(self.tree.statistics(), original)
        self.assertEqual(self.tree.find(10), 0)

    def test_many_insertions(self):
        ids = list(range(100, 0, -1))

        for position, client_id in enumerate(ids):
            self.tree.insert(client_id, position)

        for position, client_id in enumerate(ids):
            self.assertEqual(
                self.tree.find(client_id),
                position
            )

        self.assertIsNone(self.tree.find(101))

    def test_insert_stores_position_not_record(self):
        self.tree.insert(10, 7)

        self.assertEqual(self.tree.root.keys, [10])
        self.assertEqual(self.tree.root.positions, [7])

        self.assertIs(type(self.tree.root.positions[0]), int)
        self.assertFalse(hasattr(self.tree.root, "records"))

    def test_rejects_invalid_id(self):
        for client_id in [None, "10", True, 10.5, {}]:
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    self.tree.insert(client_id, 0)

        self.assertEqual(self.tree.statistics()["size"], 0)

    def test_rejects_invalid_position(self):
        for position in [-1, None, "0", True, 1.5, {}]:
            with self.subTest(position=position):
                with self.assertRaises(ValueError):
                    self.tree.insert(10, position)

        self.assertEqual(self.tree.statistics()["size"], 0)


class BTreeInvariantTests(unittest.TestCase):

    def assert_valid_tree(self, tree, expected_positions):
        t = tree.min_degree
        leaf_depths = set()
        found_keys = set()

        def check_node(node, minimum, maximum, depth, is_root=False):
            key_count = len(node.keys)

            self.assertEqual(key_count, len(node.positions))

            self.assertLessEqual(key_count, 2 * t - 1)

            if not is_root:
                self.assertGreaterEqual(key_count, t - 1)

            elif not node.leaf:
                self.assertGreaterEqual(key_count, 1)

            self.assertEqual(node.keys, sorted(node.keys))

            for index, key in enumerate(node.keys):
                position = node.positions[index]

                self.assertIs(type(position), int)
                self.assertGreaterEqual(position, 0)

                self.assertIn(key, expected_positions)
                self.assertEqual(position, expected_positions[key])

                self.assertNotIn(key, found_keys)
                found_keys.add(key)

                if minimum is not None:
                    self.assertGreater(key, minimum)

                if maximum is not None:
                    self.assertLess(key, maximum)

                if index > 0:
                    self.assertGreater(
                        key,
                        node.keys[index - 1]
                    )

            if node.leaf:
                self.assertEqual(node.children, [])

                leaf_depths.add(depth)

                return key_count

            self.assertEqual(
                len(node.children),
                key_count + 1
            )

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
        self.assertEqual(found_keys, set(expected_positions))
        self.assertEqual(total, len(expected_positions))

        return total

    def test_preserves_invariants_with_1000_clients(self):
        for degree in [2, 3, 4]:
            for order in ["ascending", "descending", "random"]:

                with self.subTest(degree=degree, order=order):
                    tree = BTree(min_degree=degree)

                    ids = list(range(1, 1001))

                    if order == "descending":
                        ids.reverse()

                    elif order == "random":
                        random.Random(2026).shuffle(ids)

                    expected_positions = {}

                    for position, client_id in enumerate(ids):
                        tree.insert(client_id, position)

                        expected_positions[client_id] = position

                    total = self.assert_valid_tree(
                        tree,
                        expected_positions
                    )

                    self.assertEqual(total, 1000)

                    for client_id in range(1, 1001):
                        self.assertEqual(
                            tree.find(client_id),
                            expected_positions[client_id]
                        )

                    self.assertIsNone(tree.find(1001))

    def test_preserves_invariants_after_every_insertion(self):
        tree = BTree(min_degree=3)

        ids = list(range(1, 121))
        random.Random(42).shuffle(ids)

        expected_positions = {}

        for position, client_id in enumerate(ids):
            tree.insert(client_id, position)

            expected_positions[client_id] = position

            total = self.assert_valid_tree(
                tree,
                expected_positions
            )

            self.assertEqual(total, position + 1)


class BTreeTraversalTests(unittest.TestCase):

    def setUp(self):
        self.tree = BTree(min_degree=3)

    def test_empty_tree_returns_empty_list(self):
        self.assertEqual(self.tree.list_all(), [])

    def test_list_all_returns_positions_in_key_order(self):
        ids = [50, 10, 80, 30, 20, 70, 40, 60]

        for position, client_id in enumerate(ids):
            self.tree.insert(client_id, position)

        positions = self.tree.list_all()

        self.assertEqual(
            positions,
            [1, 4, 3, 6, 0, 7, 5, 2]
        )

        result_ids = [
            ids[position]
            for position in positions
        ]

        self.assertEqual(result_ids, sorted(ids))

    def test_list_all_returns_independent_list(self):
        self.tree.insert(10, 0)
        self.tree.insert(20, 1)

        positions = self.tree.list_all()

        positions[0] = 999
        positions.append(500)

        self.assertEqual(self.tree.list_all(), [0, 1])
        self.assertEqual(self.tree.find(10), 0)

    def test_list_all_with_1000_clients(self):
        ids = list(range(1, 1001))

        random.Random(2026).shuffle(ids)

        for position, client_id in enumerate(ids):
            self.tree.insert(client_id, position)

        positions = self.tree.list_all()

        result_ids = [
            ids[position]
            for position in positions
        ]

        self.assertEqual(len(positions), 1000)

        self.assertEqual(
            result_ids,
            list(range(1, 1001))
        )


class BTreeStatisticsTests(unittest.TestCase):

    def test_empty_tree_statistics(self):
        tree = BTree()

        self.assertEqual(
            tree.statistics(),
            {
                "size": 0,
                "height": 0,
                "node_count": 0,
                "splits": 0,
                "lookups": 0,
            }
        )

    def test_statistics_after_operations(self):
        tree = BTree(min_degree=3)

        ids = [10, 20, 30, 40, 50, 60]

        for position, client_id in enumerate(ids):
            tree.insert(client_id, position)

        stats = tree.statistics()

        self.assertEqual(stats["size"], 6)
        self.assertEqual(stats["height"], 2)
        self.assertEqual(stats["node_count"], 3)
        self.assertEqual(stats["splits"], 1)
        self.assertEqual(stats["lookups"], 0)

        tree.find(10)
        tree.find(999)

        self.assertEqual(
            tree.statistics()["lookups"],
            2
        )

        with self.assertRaises(ValueError):
            tree.insert(10, 7)

        self.assertEqual(
            tree.statistics()["size"],
            6
        )

        self.assertEqual(
            tree.statistics()["lookups"],
            2
        )

    def test_list_all_does_not_change_statistics(self):
        tree = BTree()

        tree.insert(30, 0)
        tree.insert(10, 1)
        tree.insert(20, 2)

        before = tree.statistics()

        tree.list_all()

        self.assertEqual(tree.statistics(), before)


if __name__ == "__main__":
    unittest.main()