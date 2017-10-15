import pickle
import numpy as np
from gensim import corpora, models, matutils
from semantic_selector import tokenizer


class Vectorizer:
    def __init__(self, records, dictionary=None, label_types=None):
        (self.word_vecs, labels) = self.convert_to_word_vecs(records)

        # set input dimension of NN
        if dictionary is None:
            self.dictionary = corpora.Dictionary(self.word_vecs)
            with open("inputs.dict","wb") as f:
                self.dictionary.save(f)
        else:
            self.dictionary = dictionary

        if label_types is None:
            self.label_types = list(set(labels))
        else:
            self.label_types = label_types
            with open("labels.pickle","wb") as f:
                pickle.dump(self.label_types, f)

        self.num_terms = len(self.dictionary.keys())
        print("num_terms (input dim):", self.num_terms)

        # set output dimension of NN
        self.num_classes = len(self.label_types)
        print("num_classes (output dim):", self.num_classes)

        # generate numpy arrays
        self.x = self.convert_to_numpy_vecs(self.word_vecs)

        # annotation vectors
        y = [self.label_types.index(x) for x in labels]
        self.y = np.asarray(y, dtype=np.float32)

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
