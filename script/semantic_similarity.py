import re
import os
import mysql.connector
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities
from sklearn.linear_model import LogisticRegression


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
              'id',
              'value',
              'alt',
              'placeholder']:
        if (k not in s.attrs) or (s.attrs[k] == ''):
            continue

        for token in preprocess(s.attrs[k]):
            words.append(token)

    return words


def sparse_to_dense(vec):
    ret = [e[1] for e in vec]
    return ret

class LsiModel:
    def __init__(self, answers, labels):
        self.answers = answers

        dictionary = corpora.Dictionary(answers)
        corpus = [dictionary.doc2bow(answer) for answer in answers]
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=15)

        lsi_corpus_flattened = []
        for lsi_vec in lsi[corpus]:
            lsi_corpus_flattened.append(sparse_to_dense(lsi_vec))

        lr = LogisticRegression(solver='newton-cg', max_iter=10000, multi_class='ovr')
        lr.fit(X=lsi_corpus_flattened, y=labels)
        print("fitting score: ", lr.score(X=lsi_corpus_flattened, y=labels))

        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.lr = lr

    def inference(self, target_tag):
        vec_bow = self.dictionary.doc2bow(get_attrs_value(target_tag))
        vec_lsi = sparse_to_dense(self.lsi[vec_bow])
        return self.lr.predict([vec_lsi])


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


def main():
    records = fetch_all('inputs')
    answers = []
    labels = []
    for r in records:
        words = get_attrs_value(r['html'])
        answers.append(words)
        labels.append(to_label_id(r['label']))

    model = LsiModel(answers, labels)

    test_records = fetch_all('test_inputs')

    hit = 0
    login_e_cnt = 0
    login_c_cnt = 0
    login_ec_cnt = 0
    password_e_cnt = 0
    password_c_cnt = 0
    password_ec_cnt = 0
    for t in test_records:
        target_tag = t['html']
        estimated_label = to_label(model.inference(target_tag))
        correct_label = t['label']
        print("test tag:", t['html'])
        print("estimated, correct:", estimated_label, correct_label)

        if estimated_label == correct_label:
            hit += 1

        if estimated_label == 'login_id':
            login_e_cnt +=1
        if correct_label == 'login_id':
            login_c_cnt += 1
        if estimated_label == 'login_id' and correct_label == 'login_id':
            login_ec_cnt += 1

        if estimated_label == 'password':
            password_e_cnt +=1
        if correct_label == 'password':
            password_c_cnt += 1
        if estimated_label == 'password' and correct_label == 'password':
            password_ec_cnt += 1

    print("\nEvaluation")
    print("Precision(login): ", (login_ec_cnt / login_e_cnt))
    print("Recall(login): ", (login_ec_cnt / login_c_cnt))
    print("Precision(password): ", (password_ec_cnt / password_e_cnt))
    print("Recall(password): ", (password_ec_cnt / password_c_cnt))
    print("Total Accuracy: ", (hit / len(test_records)))


if __name__ == '__main__':
    main()
