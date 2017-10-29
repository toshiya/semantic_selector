import unittest
from mock import mock
from sqlalchemy import create_engine, func, sql
from semantic_selector import datasource
from sqlalchemy.orm import sessionmaker

class TestDatasource(unittest.TestCase):

    def test_read_canonical_topics(self):
        c = datasource.read_canonical_topics()
        self.assertEqual(len(c.keys()), 116)

    def test_fetch_data(self):
        dummy = [
                    datasource.Input(id=1, url='url', html='html', \
                                     parent_html='parent_html', topic='topic'),
                    datasource.Input(id=2, url='url', html='html', \
                                     parent_html='parent_html', topic='topic')
                ]
        input_tags = datasource.InputTags(exclude_threshold=0)
        with mock.patch.object(input_tags, 'query', return_value=dummy) as method:
            (training, tests) = input_tags.fetch_data(ratio_test_data=0, seed=100)
            self.assertEqual(len(training), 2)
            self.assertEqual(len(tests), 0)
            method.assert_called_once()

if __name__ == '__main__':
    unittest.main()
