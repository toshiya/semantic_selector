# -*- coding: utf-8 -*-
import random
import time
from gensim import corpora, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import tokenizer
from semantic_selector import datasource


class LsiModel(object):

    def __init__(self, test_data_ratio=0, grouping=None):
        random.seed(int(time.time()))
        self.num_topics = 500
        self.ratio_test_data = test_data_ratio
        self.training_data_table = 'inputs'
        self.lr_solver = 'newton-cg'
        self.lr_max_iter = 10000
        self.lr_multi_class = 'ovr'
        self.grouping = grouping

        import pdb; pdb.set_trace();
        (records,
         grouped_labels,
         grouped_label_types) = self.__fetch_training_data()
        self.answers = [r['words'] for r in records]
        self.grouped_label_types = grouped_label_types
        self.grouped_label_ids = [
                self.grouped_label_id(x) for x in grouped_labels
                ]

        self.num_test_data = int(len(self.answers) * self.ratio_test_data)
        self.test_data = []
        for r in range(self.num_test_data):
            random_index = random.randint(0, len(self.answers) - 1)
            if self.answers[random_index]:
                self.test_data.append(records[random_index])
                del self.answers[random_index]
                del self.grouped_label_ids[random_index]

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
        lr.fit(X=lsi_corpus_flattened, y=self.grouped_label_ids)

        self.fitting_score = lr.score(X=lsi_corpus_flattened,
                                      y=self.grouped_label_ids)
        self.dictionary = dictionary
        self.corpus = corpus
        self.lsi = lsi
        self.lr = lr

    def inference_html(self, target_tag):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        tokens = input_tag_tokenizer.get_attrs_value(target_tag)
        vec_bow = self.dictionary.doc2bow(tokens)
        vec_lsi = self.__sparse_to_dense(self.lsi[vec_bow])
        if len(vec_lsi) == 0:
            return 'unknown'
        else:
            predict_value = self.lr.predict([vec_lsi])[0]
            return self.grouped_label_name_from_id(predict_value)

    def grouped_label_id(self, label_name):
        grouped_label_name = self.grouped_label_name(label_name)
        return self.grouped_label_types.index(grouped_label_name)

    def grouped_label_name_from_id(self, label_id):
        return self.grouped_label_types[label_id]

    def grouped_label_name(self, label_name):
        if not self.grouping:
            return label_name
        else:
            if label_name in self.grouping:
                return self.grouping[label_name]
            else:
                return label_name

    def __sparse_to_dense(self, vec):
        ret = [0 for e in range(self.num_topics)]
        for v in vec:
            ret[v[0]] = v[1]
        return ret

    def __fetch_training_data(self):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        input_tags = datasource.InputTags()
        records = input_tags.fetch_all(self.training_data_table)
        labels = []
        for r in records:
            words = input_tag_tokenizer.get_attrs_value(r['html'])
            r['words'] = words
            labels.append(r['label'])
        grouped_labels = [self.grouped_label_name(l) for l in labels]
        grouped_label_types = list(set(grouped_labels))
        return (records, labels, grouped_label_types)


if __name__ == "__main__":
    print("machine learning model")
