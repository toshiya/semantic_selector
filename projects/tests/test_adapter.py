import unittest
from mock import mock
from semantic_selector.mysql import Input
from semantic_selector.tokenizer import InputTagTokenizer
from semantic_selector.adapter.training import MySQLTrainingAdapter


class TestMySQLTrainingAdapter(unittest.TestCase):

    def setUp(self):
        InputTagTokenizer()

    @mock.patch('semantic_selector.mysql.InputTable.fetch_data')
    @mock.patch('semantic_selector.tokenizer.'
                'InputTagTokenizer.get_attrs_value')
    def test_generate_training_data(self,
                                    mock_get_attrs_value,
                                    mock_fetch_data):

        data = [Input(id=1, url='url', html='html',
                      parent_html='parent_html', topic='pc_email'),
                Input(id=2, url='url', html='html',
                      parent_html='parent_html', topic='password'),
                Input(id=3, url='url2', html='html',
                      parent_html='parent_html', topic='pc_email'),
                Input(id=4, url='url3', html='html',
                      parent_html='parent_html', topic='pc_email')]

        mock_get_attrs_value.return_value = ["a", "b"]
        mock_fetch_data.return_value = data

        options = {'ratio_test': 0.4, 'threashold': 0, 'seed': 100}
        adapter = MySQLTrainingAdapter(options)
        self.assertEqual(len(adapter.dictionary.keys()), 2)
        self.assertTrue('a' in list(adapter.dictionary.values()))
        self.assertTrue('b' in list(adapter.dictionary.values()))

        self.assertEqual(len(adapter.all_topics), 2)
        self.assertTrue('email' in list(adapter.all_topics))
        self.assertTrue('password' in list(adapter.all_topics))

        # check test selection logic
        self.assertEqual(len(adapter.be_train), 2)
        self.assertEqual(len(adapter.be_train[0]), 2)
        self.assertEqual(len(adapter.be_train[1]), 1)

        self.assertEqual(len(adapter.be_test), 1)
        self.assertEqual(len(adapter.be_test[0]), 1)

        self.assertEqual(len(adapter.ot_train), 2)
        self.assertEqual(len(adapter.ot_train[0]), 2)
        self.assertEqual(len(adapter.ot_train[1]), 1)

        self.assertEqual(len(adapter.ot_test), 1)
        self.assertEqual(len(adapter.ot_test[0]), 1)


if __name__ == '__main__':
    unittest.main()
