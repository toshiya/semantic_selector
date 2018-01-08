import pickle
from sklearn.linear_model import LogisticRegression
from gensim import models, matutils
from .base import BaseEstimator


class LsiEstimator(BaseEstimator):
    def __init__(self):
        super().__init__()
        self.hidden_size = 500
        self.lr_solver = 'newton-cg'
        self.lr_max_iter = 10000
        self.lr_multi_class = 'ovr'
        self.lsi_filename = "/lsi"
        self.lr_filename = "/lr.pickle"

    def train(self, options=None):
        if self.adapter is None:
            raise "please set adapter before training"
        adapter = self.adapter

        lsi = self.__make_lsi(adapter)
        x_train = self.__make_x(lsi, adapter.be_train)
        y_train = self.__make_y(adapter.ot_train)
        x_test = self.__make_x(lsi, adapter.be_test)
        y_test = self.__make_y(adapter.ot_test)

        print("Train samples: ", len(x_train))
        print("Validation samples: ", len(x_test))

        lr = LogisticRegression(solver=self.lr_solver,
                                max_iter=self.lr_max_iter,
                                multi_class=self.lr_multi_class)
        lr.fit(X=x_train, y=y_train)
        self.lsi = lsi
        self.lr = lr

        print("Train :", lr.score(X=x_train, y=y_train))
        print("Validation :", lr.score(X=x_test, y=y_test))

        print('Validation Acuracy', self.calc_accuracy(x_test, y_test))

    def predict(self):
        be_infer = self.adapter.get_bow_element_vectors()
        x_infer = self.__make_x(self.lsi, be_infer)
        topic_id = self.predict_x(x_infer[0])
        return self.all_topics[topic_id]

    def predict_x(self, x):
        return self.lr.predict([x])[0]

    def load_model(self, path):
        self.lsi = models.LsiModel.load(path + self.lsi_filename)
        with open(path + self.lr_filename, "rb") as f:
            self.lr = pickle.load(f)

    def save_model(self, path):
        self.lsi.save(path + self.lsi_filename)
        with open(path + self.lr_filename, "wb") as f:
            pickle.dump(self.lr, f)

    def __make_lsi(self, adapter):
        raw_corpus = []
        for x in adapter.be_train:
            raw_corpus.extend(matutils.Dense2Corpus(x.T))
        lsi = models.LsiModel(raw_corpus,
                              id2word=adapter.dictionary,
                              num_topics=self.hidden_size)
        return lsi

    def __make_x(self, lsi, vecs):
        corpus = []
        for x in vecs:
            corpus.extend(matutils.Dense2Corpus(x.T))
        x = []
        for vec in lsi[corpus]:
            x.append(self.__sparse_to_dense(vec))
        return x

    def __make_y(self, vecs):
        """
        convert array of one hot vectors to array of integer
        """
        flatten_vecs = []
        for x in vecs:
            flatten_vecs.extend(x)
        return [v.argmax() for v in flatten_vecs]

    def __sparse_to_dense(self, vec):
        ret = [0 for e in range(self.hidden_size)]
        for v in vec:
            ret[v[0]] = v[1]
        return ret
