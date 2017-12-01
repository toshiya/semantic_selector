import unittest
from semantic_selector.adapter.many_to_many import JSONTrainingAdapter


class TestJSONTrainingAdapter(unittest.TestCase):
    email_html = "<input type='text' name='mail_addr' placeholder='メールアドレス'>"
    password_html = "<input type='password' name='pass' placeholder='パスワード'>"

    data = { "train": [
                        {
                            'id': 1,
                            'title': 'site1',
                            'url': "http//example1.com/register",
                            'html': email_html,
                            'canonical_topic': 'email',
                        },
                        {
                            'id': 2,
                            'title': 'site1',
                            'url': "http//example1.com/register",
                            'html': password_html,
                            'canonical_topic': 'password',
                        },
                        {
                            'id': 3,
                            'title': 'site2',
                            'url': "http//example2.com/register",
                            'html': email_html,
                            'canonical_topic': 'password',
                        },
                        {
                            'id': 4,
                            'title': 'site3',
                            'url': "http//example3.com/register",
                            'html': email_html,
                            'canonical_topic': 'password',
                        },
                    ],
             "test": [],
            }


    def SetUp(self):
        InputTagTokenizer()


    def test_generate_training_data(self):
        options = {
            'ratio_test': 0.0,
            'seed': 100,
            'samples': TestJSONTrainingAdapter.data
        }
        adapter = JSONTrainingAdapter(options)

        dict_size = adapter.dictionary.keys()
        self.assertEqual(dict_size, 7)

        max_num_input_tags = adapter.max_num_input_tags
        self.assertEqual(max_num_input_tags, 2)

        self.assertEqual(adapter.x_train.shape, (3, max_num_input_tags, 7))


if __name__ == '__main__':
    unittest.main()
