import unittest
from semantic_selector.csv import CanonicalTopicTable 

class TestCsv(unittest.TestCase):
    def test_read_canonical_topics(self):
        c = CanonicalTopicTable().get()
        self.assertEqual(len(c.keys()), 116)


if __name__ == '__main__':
    unittest.main()
