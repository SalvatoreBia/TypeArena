import random

class RandomTextGenerator:
    en_dict_path = 'model/dictionaries/en/words.txt'
    it_dict_path = 'model/dictionaries/it/1000_parole_italiane_comuni.txt'

    
    def _load_dictionary(path):
        words = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w and not w.startswith('//'):
                    words.append(w)
        return words

    @classmethod
    def generate_text(cls, language='it', word_count=100):
        if language == 'en':
            dict_path = cls.en_dict_path
        elif language == 'it':
            dict_path = cls.it_dict_path
        else:
            raise ValueError("Language must be 'en' or 'it'")
        words_list = cls._load_dictionary(dict_path)
        chosen_words = random.choices(words_list, k=word_count)
        return ' '.join(chosen_words)

if __name__ == "__main__":
    print(RandomTextGenerator.generate_random_phrase('it', 10))