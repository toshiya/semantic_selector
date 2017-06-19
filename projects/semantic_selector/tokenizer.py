# -*- coding: utf-8 -*-
import re
import MeCab
from bs4 import BeautifulSoup


class InputTagTokenizer(object):
    class __InputTagTokenizer(object):
        def __init__(self):
            self.tokenizer = MeCab.Tagger("")
            # Work Around for mecab-python3 bug
            # https://shogo82148.github.io/blog/2015/12/20/mecab-in-python3-final/
            self.tokenizer.parse('')
            self.target_attributes = [
                    'name',
                    'type',
                    'id',
                    'value',
                    'alt',
                    'placeholder'
                    ]

        def mecab_tokenize(self, text):
            ret = []
            node = self.tokenizer.parseToNode(text)
            while node:
                feats = node.feature.split(",")
                if feats[0] in ['名詞']:
                    ret.append(node.surface)
                node = node.next
            return ret

        def get_attrs_value(self, html):
            words = []
            html_soup = BeautifulSoup(html, 'html.parser')
            s = html_soup.find('input')
            for k in self.target_attributes:
                if (k not in s.attrs) or (s.attrs[k] == ''):
                    continue

                for token in self.__preprocess(s.attrs[k]):
                    words.append(token)

            return words

        def __convert_to_snake(self, name):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        def __preprocess(self, value):
            snake_case_value = self.__convert_to_snake(value)
            snake_case_value = re.sub(r'([0-9]+)', r'_\1', snake_case_value)
            tokens = re.split(r'[-_\]\[ ]', snake_case_value)
            for t in tokens:
                japanese_tokens = self.mecab_tokenize(t)
                for j_t in japanese_tokens:
                    if j_t == "\n":
                        continue
                    yield j_t

    instance = None

    def __init__(self):
        if not InputTagTokenizer.instance:
            singleton_instance = InputTagTokenizer.__InputTagTokenizer()
            InputTagTokenizer.instance = singleton_instance

    def __getattr__(self, name):
        return getattr(self.instance, name)


if __name__ == "__main__":
    print("preprocessor")
