import re
import os
import mysql.connector
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities

import MeCab
_MECAB_TOKENIZER = MeCab.Tagger("-Owakati")
# Work Around for mecab-python3 bug
# https://shogo82148.github.io/blog/2015/12/20/mecab-in-python3-final/
_MECAB_TOKENIZER.parse('')


def fetch_all(table_name):
    db_password = 'root'
    if 'DB_PASSWORD' in os.environ:
        db_password = os.environ['DB_PASSWORD']
    conn = mysql.connector.connect(
            user='root',
            password=db_password,
            host='localhost',
            database='login_form'
            )
    cursor = conn.cursor(dictionary=True)
    stmt = "SELECT * FROM " + table_name
    cursor.execute(stmt)
    records = cursor.fetchall()
    conn.close()
    return records


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
              'value',
              'id',
              'alt',
              'placeholder']:
        if (k not in s.attrs) or (s.attrs[k] == ''):
            continue

        for token in preprocess(s.attrs[k]):
            words.append(token)
    return words


class LsiModel:
    def __init__(self, answers):
        self.answers = answers

        dictionary = corpora.Dictionary(answers)
        corpus = [dictionary.doc2bow(answer) for answer in answers]
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=5)
        index = similarities.MatrixSimilarity(lsi[corpus])

        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.index = index

    def get_similar_inputs(self, target_tag):
        vec_bow = self.dictionary.doc2bow(get_attrs_value(target_tag))
        vec_lsi = self.lsi[vec_bow]
        sims = self.index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims


def output(test_record, records, similarities):
    print('URL: ' + test_record['url'])
    print('target tag: ' + test_record['html'])
    labels = []
    for i in range(0, 5):
        r = records[similarities[i][0]]
        labels.append(r['label'])
    num_labels = {}
    for label in labels:
        if label not in num_labels:
            num_labels[label] = 1
        else:
            num_labels[label] += 1
    max_key = max(num_labels.keys(), key=lambda item: num_labels[item])
    print('estimated label: ' + max_key)
    print('answer label:' + test_record['label'])


def main():
    records = fetch_all('inputs')
    answers = []
    for r in records:
        words = get_attrs_value(r['html'])
        answers.append(words)

    model = LsiModel(answers)

    test_records = fetch_all('test_inputs')
    for t in test_records:
        target_tag = t['html']
        t_label = t['label']
        similarities = model.get_similar_inputs(target_tag)
        output(t, records, similarities)
        print()


if __name__ == '__main__':
    main()
