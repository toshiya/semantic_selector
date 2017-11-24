import unittest
from mock import mock
from semantic_selector.mysql import Input, InputTable


class TestMysql(unittest.TestCase):
    @mock.patch('semantic_selector.mysql.InputTable.query')
    def test_fetch_data(self, mock_query):
        dummy = [
                    Input(id=1, url='url', html='html',
                          parent_html='parent_html', topic='topic'),
                    Input(id=2, url='url', html='html',
                          parent_html='parent_html', topic='topic')
                ]
        mock_query.return_value = dummy
        input_table = InputTable(exclude_threshold=0)
        (training, tests) = input_table.fetch_data(ratio_test_data=0,
                                                   seed=100)
        self.assertEqual(len(training), 2)
        self.assertEqual(len(tests), 0)


if __name__ == '__main__':
    unittest.main()
