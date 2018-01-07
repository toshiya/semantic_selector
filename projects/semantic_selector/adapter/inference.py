from abc import abstractmethod
from .base import Adapter


class InferenceAdapter(Adapter):
    def __init__(self, options):
        super().__init__()
        self.options = options

    @abstractmethod
    def get_bow_element_vectors(self):
        pass


class JSONInferenceAdapter(InferenceAdapter):
    def get_bow_element_vectors(self):
        record = self.options['record']
        word_vecs = self.convert_to_word_vecs([record])
        return self.to_bow_element_vectors(self.dictionary, word_vecs)
