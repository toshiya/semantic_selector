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


def get_attrs_value(html):
    words = []
    soup = BeautifulSoup(html, 'html.parser')
    s = soup.find('input')
    for k in ['name', 'type', 'value', 'id', 'alt', 'placeholder']:
        if (k in s.attrs) and (s.attrs[k] != ''):
            preprocessed_value = re.sub(r'[0-9]', '', convert_to_snake(s.attrs[k]))
            tokens = re.split(r'[-_\]\[ ]', preprocessed_value)
            for t in tokens:
                p_t = _MECAB_TOKENIZER.parse(t).split(' ')
                words.extend(p_t[:-1])
    return words


class LsiModel:
    def __init__(self, answers):
        self.answers = answers
        self.dictionary = corpora.Dictionary(answers)
        self.corpus = [self.dictionary.doc2bow(answer) for answer in answers]
        self.lsi = models.LsiModel(self.corpus, id2word=self.dictionary, num_topics=5)
        self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])

    def get_similar_inputs(self, target_tag):
        vec_bow = self.dictionary.doc2bow(get_attrs_value(target_tag))
        vec_lsi = self.lsi[vec_bow]
        sims = self.index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims


def output(test_record, records, similarities):
    print('URL: ' + test_record['url'])
    print('target tag: ' + test_record['html'])
    # for debug 
    #print('target words:' + " ".join(get_attrs_value(test_record['html']))) 
    labels = []
    for i in range(0, 5):
        r = records[similarities[i][0]]
        labels.append(r['label'])
        # for debug 
        #print('label:' + r['label'] + ' url:' + r['url'] + ' html:' + r['html'] + ' words:' + " ".join(get_attrs_value(r['html'])) + 'similarity: ' + str(similarities[i][1]))
    num_labels = {}
    for label in labels:
        if label not in num_labels:
            num_labels[label] = 1
        else:
            num_labels[label] += 1
    max_key = max(num_labels.keys(), key=lambda item:num_labels[item])
    #print('similar labels: ', end='')
    #print(num_labels)
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
