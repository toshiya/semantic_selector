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
        raw_data = input_table.fetch_data()
        self.assertEqual(len(raw_data), 2)


if __name__ == '__main__':
    unittest.main()
