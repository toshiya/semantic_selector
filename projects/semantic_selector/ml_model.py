from gensim import corpora, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import preprocessor


class LsiModel:
    def __init__(self, answers, labels):
        self.answers = answers

        dictionary = corpora.Dictionary(answers)
        corpus = [dictionary.doc2bow(answer) for answer in answers]
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=15)

        lsi_corpus_flattened = []
        for lsi_vec in lsi[corpus]:
            lsi_corpus_flattened.append(self.__sparse_to_dense(lsi_vec))

        lr = LogisticRegression(solver='newton-cg', max_iter=10000, multi_class='ovr')
        lr.fit(X=lsi_corpus_flattened, y=labels)
        print("fitting score: ", lr.score(X=lsi_corpus_flattened, y=labels))

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


if __name__ == "__main__":
    print("machine learning model")
