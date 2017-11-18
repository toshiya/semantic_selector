import unittest
from mock import mock
from sqlalchemy import create_engine, func, sql
from semantic_selector.mysql import Input, InputTable
from sqlalchemy.orm import sessionmaker

class TestMysql(unittest.TestCase):
    def test_fetch_data(self):
        dummy = [
                    Input(id=1, url='url', html='html', \
                                     parent_html='parent_html', topic='topic'),
                    Input(id=2, url='url', html='html', \
                                     parent_html='parent_html', topic='topic')
                ]
        input_table = InputTable(exclude_threshold=0)
        with mock.patch.object(input_table, 'query', return_value=dummy) as method:
            (training, tests) = input_table.fetch_data(ratio_test_data=0, seed=100)
            self.assertEqual(len(training), 2)
            self.assertEqual(len(tests), 0)
            method.assert_called_once()

if __name__ == '__main__':
    unittest.main()
