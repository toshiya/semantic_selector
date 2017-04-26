import re
import os
import mysql.connector
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities

import MeCab
# Work Around for mecab-python3 bug
# https://github.com/KosukeArima/next/issues/18
_MECAB_TOKENIZER = MeCab.Tagger("-Owakati")

# https://shogo82148.github.io/blog/2015/12/20/mecab-in-python3-final/
_MECAB_TOKENIZER.parse('')

# TODO:
# read from input file
mobage_loginid = """
<input type="email" id="mail-address" name="mail_address" placeholder="mangabox@abc.com">
"""

#<input class="mypage_input" type="text" placeholder="ニックネーム(半角英数字3文字以上16文字以内)" name="nickname" value="">

def get_inputs():
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
    cursor.execute('SELECT * FROM inputs')
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
    for k in ['name', 'value', 'id', 'alt', 'placeholder']:
        if (k in s.attrs) and (s.attrs[k] != ''):
            preprocessed_value = re.sub(r'[0-9]', '', convert_to_snake(s.attrs[k]))
            tokens = re.split(r'[-_\]\[ ]', preprocessed_value)
            for t in tokens:
                p_t = _MECAB_TOKENIZER.parse(t).split(' ')
                words.extend(p_t[:-1])
    return words

def get_corpus(dictionary, texts):
    corpus = [dictionary.doc2bow(text) for text in texts]
    return corpus

def get_similar_inputs(target_html, lsi, index, dictionary):
    vec_bow = dictionary.doc2bow(get_attrs_value(target_html))
    vec_lsi = lsi[vec_bow]
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return sims

def main():
    records = get_inputs()
    texts = []
    for r in records:
        words = get_attrs_value(r['html'])
        texts.append(words)

    dictionary = corpora.Dictionary(texts)
    corpus = get_corpus(dictionary, texts)

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=5)
    index = similarities.MatrixSimilarity(lsi[corpus])

    print("LoginID\n")
    # vectorize mobage input
    print('target tag: ' + mobage_loginid)
    print('target words:' + " ".join(get_attrs_value(mobage_loginid)))
    print("\n")

    print("Top 5 similar input tags")
    mobage_loginid_sims = get_similar_inputs(mobage_loginid, lsi, index, dictionary)
    for i in range(0, 5):
        r = records[mobage_loginid_sims[i][0]] 
        print('label:' + r['label'])
        print('url:' + r['url'])
        print('html:' + r['html'])
        print('words:' + " ".join(get_attrs_value(r['html'])))
        print('similarity: ' + str(mobage_loginid_sims[i][1]))
        print("\n")


if __name__ == '__main__':
    main()
