import mysql.connector
import re
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities

mobage_loginid = """
<input type="email" id="subject-id" name="subject_id" autocomplete="on" placeholder="メールアドレス" class="txtfield w-max" value="">
"""

mobage_password = """
<input type="password" id="subject-password" name="subject_password" value="" placeholder="パスワード" class="txtfield w-max m-t-s" pattern="^[A-Za-z0-9-_.@/]{4,20}$">
"""

def get_inputs():
    conn = mysql.connector.connect(
            user='root',
            password='root',
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
    for k in ['name', 'value', 'id', 'alt', 'type', 'placeholder']:
        if (k in s.attrs) and (s.attrs[k] != ''):
            tokens = re.split(r'[-_\]\[]', convert_to_snake(s.attrs[k]))
            words.extend(tokens)
    return words

def similarity(dictionary, word1, word2):
    vec1 = dictionary.doc2bow(word1)
    vec2 = dictionary.doc2bow(word2)

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

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=10)
    index = similarities.MatrixSimilarity(lsi[corpus])

    print("LoginID\n")
    # vectorize mobage input
    mobage_loginid_sims = get_similar_inputs(mobage_loginid, lsi, index, dictionary)
    for i in range(0, 5):
        r = records[mobage_loginid_sims[i][0]] 
        print('label:' + r['label'])
        print('url:' + r['url'])
        print('html:' + r['html'])
        print("\n")

    print("Password\n")
    # vectorize mobage password
    mobage_password_sims = get_similar_inputs(mobage_password, lsi, index, dictionary)
    for i in range(0, 5):
        r = records[mobage_password_sims[i][0]] 
        print('label:' + r['label'])
        print('url:' + r['url'])
        print('html:' + r['html'])
        print("\n")


if __name__ == '__main__':
    main()
