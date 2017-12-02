import unittest
from semantic_selector.tokenizer import InputTagTokenizer
from semantic_selector.adapter.many_to_many import JSONTrainingAdapter


class TestJSONTrainingAdapter(unittest.TestCase):
    email_html = "<input type='text' name='mail_addr' placeholder='メールアドレス'>"
    password_html = "<input type='password' name='pass'>"

    data = [
        {
            'id': 1,
            'title': 'site1',
            'url': "http://example1.com/register",
            'html': email_html,
            'canonical_topic': 'email',
        },
        {
            'id': 2,
            'title': 'site1',
            'url': "http://example1.com/register",
            'html': password_html,
            'canonical_topic': 'password',
        },
        {
            'id': 3,
            'title': 'site2',
            'url': "http://example2.com/register",
            'html': email_html,
            'canonical_topic': 'email',
        },
        {
            'id': 4,
            'title': 'site3',
            'url': "http://example3.com/register",
            'html': email_html,
            'canonical_topic': 'email',
        },
        {
            'id': 5,
            'title': 'site4',
            'url': "http://example4.com/register",
            'html': email_html,
            'canonical_topic': 'email',
        },
    ]

    def SetUp(self):
        InputTagTokenizer()

    def test_generate_training_data(self):
        options = {
            'ratio_test': 0.3,
            'seed': 100,
            'samples': TestJSONTrainingAdapter.data
        }
        adapter = JSONTrainingAdapter(options)

        dict_size = len(adapter.dictionary.keys())
        self.assertEqual(dict_size, 6)

        topic_size = len(adapter.topics)
        self.assertEqual(topic_size, 3)

        self.assertEqual(adapter.max_tag_count, 2)
        self.assertEqual(adapter.max_word_count, 4)

        expected_page_count = 3
        self.assertEqual(adapter.x_train.shape, (expected_page_count,
                                                 adapter.max_tag_count,
                                                 adapter.max_word_count))
        self.assertEqual(adapter.y_train.shape, (expected_page_count,
                                                 adapter.max_tag_count,
                                                 topic_size))


if __name__ == '__main__':
    unittest.main()
