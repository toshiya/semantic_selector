import numpy as np
from gensim import corpora, models, matutils
from semantic_selector import tokenizer


class Vectorizer:
    def __init__(self, training_records, test_records):
        (self.training_word_vecs,
         training_labels) = self.convert_to_word_vecs(training_records)
        (self.test_word_vecs,
         test_labels) = self.convert_to_word_vecs(test_records)

        # set input dimension of NN
        self.dictionary = corpora.Dictionary(self.training_word_vecs)
        self.num_terms = len(self.dictionary.keys())
        print("num_terms (input dim):", self.num_terms)

        # set output dimension of NN
        self.label_types = list(set(training_labels))
        self.num_classes = len(self.label_types)
        print("num_classes (output dim):", self.num_classes)

        # generate numpy arrays
        self.x_train = self.convert_to_numpy_vecs(self.training_word_vecs)
        self.x_test = self.convert_to_numpy_vecs(self.test_word_vecs)

        # annotation vectors
        self.y_train = np.asarray(
            [self.label_types.index(x) for x in training_labels],
            dtype=np.float32)
        self.y_test = np.asarray(
            [self.label_types.index(x) for x in test_labels],
            dtype=np.float32)

    def get_input_dim(self):
        return self.num_terms

    def get_output_dim(self):
        return self.num_classes

    def get_training(self):
        return (self.x_train, self.y_train)

    def get_test(self):
        return (self.x_test, self.y_test)

    def label_name_from_id(self, label_id):
        return self.label_types[label_id]

    def convert_to_word_vecs(self, records):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        word_vecs = []
        labels = []
        test_labels = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            labels.append(r.label)

        return (word_vecs, labels)

    def convert_to_numpy_vecs(self, word_vecs):
        bows = [self.dictionary.doc2bow(word_vec) for word_vec in word_vecs]
        return matutils.corpus2dense(bows, self.num_terms).T
