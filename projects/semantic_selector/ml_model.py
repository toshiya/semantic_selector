# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import tokenizer
from semantic_selector import datasource


class LsiModel(object):

    def __init__(self):
        self.num_topics = 15
        self.training_data_table = 'inputs'
        self.lr_solver = 'newton-cg'
        self.lr_max_iter = 10000
        self.lr_multi_class = 'ovr'

        (answers, labels, label_types) = self.__fetch_training_data()
        self.answers = answers
        self.label_types = label_types
        self.label_ids = [self.label_id(x) for x in labels]

        dictionary = corpora.Dictionary(self.answers)
        corpus = [dictionary.doc2bow(answer) for answer in self.answers]
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

        self.fitting_score = lr.score(X=lsi_corpus_flattened, y=self.label_ids)
        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.lr = lr

    def inference(self, target_tag):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        tokens = input_tag_tokenizer.get_attrs_value(target_tag)
        vec_bow = self.dictionary.doc2bow(tokens)
        vec_lsi = self.__sparse_to_dense(self.lsi[vec_bow])
        return self.lr.predict([vec_lsi])[0]

    def label_id(self, label_name):
        return self.label_types.index(label_name)

    def label_name(self, label_id):
        return self.label_types[label_id]

    def __sparse_to_dense(self, vec):
        ret = [e[1] for e in vec]
        return ret

    def __fetch_training_data(self):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        input_tags = datasource.InputTags()
        records = input_tags.fetch_all(self.training_data_table)
        answers = []
        labels = []
        for r in records:
            words = input_tag_tokenizer.get_attrs_value(r['html'])
            answers.append(words)
            labels.append(r['label'])
        label_types = list(set(labels))
        return (answers, labels, label_types)


if __name__ == "__main__":
    print("machine learning model")
