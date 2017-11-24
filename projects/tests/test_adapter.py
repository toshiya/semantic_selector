import unittest
from mock import mock
from semantic_selector.mysql import Input
from semantic_selector.tokenizer import InputTagTokenizer
from semantic_selector.adapter.one_to_one import MySQLTrainingAdapter


class TestMySQLTrainingAdapter(unittest.TestCase):

    def setUp(self):
        InputTagTokenizer()

    @mock.patch('semantic_selector.mysql.InputTable.fetch_data')
    @mock.patch('semantic_selector.mysql.Input.canonical_topic',
                new_callable=mock.PropertyMock)
    @mock.patch('semantic_selector.tokenizer.'
                'InputTagTokenizer.get_attrs_value')
    def test_generate_training_data(self,
                                    mock_get_attrs_value,
                                    mock_canonical_topic,
                                    mock_fetch_data):

        training = [Input(id=1, url='url', html='html',
                          parent_html='parent_html', topic='topic1'),
                    Input(id=2, url='url', html='html',
                          parent_html='parent_html', topic='topic2')]
        tests = [Input(id=3, url='url', html='html',
                       parent_html='parent_html', topic='topic1')]

        mock_get_attrs_value.return_value = ["a", "b"]
        mock_canonical_topic.return_value = "password"
        mock_fetch_data.return_value = (training, tests)

        options = {'ratio_test': 0.3, 'threashold': 0, 'seed': 100}
        adapter = MySQLTrainingAdapter(options)
        self.assertEqual(len(adapter.dictionary.keys()), 2)
        self.assertTrue('a' in list(adapter.dictionary.values()))
        self.assertTrue('b' in list(adapter.dictionary.values()))

        self.assertEqual(len(adapter.all_topics), 1)
        self.assertTrue('password' in list(adapter.all_topics))


if __name__ == '__main__':
    unittest.main()
