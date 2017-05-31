# -*- coding: utf-8 -*-
import re
import MeCab
from bs4 import BeautifulSoup

_MECAB_TOKENIZER = MeCab.Tagger("-Owakati")
# Work Around for mecab-python3 bug
# https://shogo82148.github.io/blog/2015/12/20/mecab-in-python3-final/
_MECAB_TOKENIZER.parse('')

def convert_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def preprocess(value):
    snake_case_value = convert_to_snake(value)
    snake_case_value = re.sub(r'[0-9]', '', snake_case_value)
    tokens = re.split(r'[-_\]\[ ]', snake_case_value)
    for t in tokens:
        japanese_tokens = _MECAB_TOKENIZER.parse(t).split(' ')
        for j_t in japanese_tokens:
            if j_t == "\n":
                continue
            yield j_t


def get_attrs_value(html):
    words = []
    soup = BeautifulSoup(html, 'html.parser')
    s = soup.find('input')
    for k in ['name',
              'type',
              'id',
              'value',
              'alt',
              'placeholder']:
        if (k not in s.attrs) or (s.attrs[k] == ''):
            continue

        for token in preprocess(s.attrs[k]):
            words.append(token)

    return words


def to_label_id(label):
    if label == 'login_id':
        return 0
    elif label == 'password':
        return 1
    elif label == 'other':
        return 2
    else:
        raise 'Unknown Label'


def to_label(label_id):
    if label_id == 0:
        return 'login_id'
    elif label_id == 1:
        return 'password'
    elif label_id == 2:
        return 'other'
    else:
        raise 'Unknown Label_id'


if __name__ == "__main__":
    print("preprocessor")
