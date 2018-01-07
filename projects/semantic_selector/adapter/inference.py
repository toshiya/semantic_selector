from abc import abstractmethod
from .base import Adapter


class InferenceAdapter(Adapter):
    def __init__(self, options):
        self.be_infer = self.generate_infered_data(options)

    @abstractmethod
    def generate_infered_data(self, options):
        pass


class JSONInferenceAdapter(InferenceAdapter):
    def generate_infered_data(self, options):
        record = options['record']
        dictionary = options['dictionary']
        word_vecs = self.convert_to_word_vecs([record])
        return self.to_bow_element_vectors(dictionary, word_vecs)
