# -*- coding: utf-8 -*-
from gensim import corpora, models
from sklearn.linear_model import LogisticRegression
from semantic_selector import tokenizer
from semantic_selector import datasource


class LsiModel(object):

    def __init__(self, training):
        self.num_topics = 500
        self.lr_solver = 'newton-cg'
        self.lr_max_iter = 10000
        self.lr_multi_class = 'ovr'

        (self.word_vecs,
         self.label_ids,
         self.label_types) = self.__convert_training(training)

        dictionary = corpora.Dictionary(self.word_vecs)
        dictionary.save_as_text("words.txt")
        corpus = [dictionary.doc2bow(word_vec) for word_vec in self.word_vecs]
        lsi = models.LsiModel(corpus,
                              id2word=dictionary,
                              num_topics=self.num_topics)

        lsi_corpus_flattened = []
        for vec in lsi[corpus]:
            lsi_corpus_flattened.append(self.__sparse_to_dense(vec))

        lr = LogisticRegression(solver=self.lr_solver,
                                max_iter=self.lr_max_iter,
                                multi_class=self.lr_multi_class)
        lr.fit(X=lsi_corpus_flattened, y=self.label_ids)

        self.fitting_score = lr.score(X=lsi_corpus_flattened,
                                      y=self.label_ids)
        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.lr = lr

    def inference_html(self, tag):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        tokens = input_tag_tokenizer.get_attrs_value(tag.html)
        vec_bow = self.dictionary.doc2bow(tokens)
        vec_lsi = self.__sparse_to_dense(self.lsi[vec_bow])
        if len(vec_lsi) == 0:
            return 'unknown'
        else:
            predict_value = self.lr.predict([vec_lsi])[0]
            return self._label_name_from_id(predict_value)

    def _label_name_from_id(self, label_id):
        return self.label_types[label_id]

    def __sparse_to_dense(self, vec):
        ret = [0 for e in range(self.num_topics)]
        for v in vec:
            ret[v[0]] = v[1]
        return ret

    def __convert_training(self, training):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        word_vecs = []
        labels = []
        test_labels = []
        for r in training:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            labels.append(r.label)

        label_types = list(set(labels))
        label_ids = [label_types.index(x) for x in labels]

        return (word_vecs, label_ids, label_types)


if __name__ == "__main__":
    print("machine learning model")
