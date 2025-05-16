import yaml
from utils.parameters import ParameterManager
import random


class WordGenerator:
    def __init__(self):
        self.tests = {}
        self.params = ParameterManager()
        self._load()

    def _load(self):
        paths = self.params.get('game', 'word_list_files')
        names = self.params.get('game', 'word_list_names')
        self.tests = dict(zip(names, paths))

    def get_words(self, list_name='english', how_many=100):
        if list_name not in self.tests:
            raise ValueError(f"The word list '{list_name}' doesn't exist.")

        if how_many < 0:
            raise ValueError('Invalid size for words list requested.')

        with open(self.tests[list_name], 'r') as file:
            words = [line.strip() for line in file if line.strip()]

        # if not words:
        #    raise Exception(f"The word list '{list_name}' is empty.")

        sampled_words = random.choices(words, k=how_many)
        return sampled_words


        