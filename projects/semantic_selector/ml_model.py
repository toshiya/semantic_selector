# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import preprocessor
from semantic_selector import datasource


class LsiModel:
    def __init__(self):
        (self.answers, self.labels) = self.__fetch_training_data()
        self.num_topics = 15

        dictionary = corpora.Dictionary(self.answers)
        corpus = [dictionary.doc2bow(answer) for answer in self.answers]
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=self.num_topics)

        lsi_corpus_flattened = []
        for lsi_vec in lsi[corpus]:
            lsi_corpus_flattened.append(self.__sparse_to_dense(lsi_vec))

        lr = LogisticRegression(solver='newton-cg', max_iter=10000, multi_class='ovr')
        lr.fit(X=lsi_corpus_flattened, y=self.labels)

        self.fitting_score = lr.score(X=lsi_corpus_flattened, y=self.labels)
        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.lr = lr

    def inference(self, target_tag):
        vec_bow = self.dictionary.doc2bow(preprocessor.get_attrs_value(target_tag))
        vec_lsi = self.__sparse_to_dense(self.lsi[vec_bow])
        return self.lr.predict([vec_lsi])

    def __sparse_to_dense(self, vec):
        ret = [e[1] for e in vec]
        return ret

    def __fetch_training_data(self):
        records = datasource.fetch_all('inputs')
        answers = []
        labels = []
        for r in records:
            words = preprocessor.get_attrs_value(r['html'])
            answers.append(words)
            labels.append(preprocessor.to_label_id(r['label']))
        return (answers, labels)


if __name__ == "__main__":
    print("machine learning model")
