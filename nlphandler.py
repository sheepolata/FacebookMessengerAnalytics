import spacy

class NLPHandler(object):
    """docstring for NLPHandler"""
    def __init__(self):
        super(NLPHandler, self).__init__()

        self.nlps = {}

        print("Loading Spacy en_core_web_lg...", flush=True, end='\r')
        self.nlps["EN"] = spacy.load("en_core_web_lg")
        print("Loading Spacy en_core_web_lg... Done!")

        print("Loading Spacy fr_core_news_md...", flush=True, end='\r')
        self.nlps["FR"] = spacy.load("fr_core_news_md")
        print("Loading Spacy fr_core_news_md... Done!")


    def is_word_french(self, word):
        return word in self.nlps["EN"].vocab

    def is_word_english(self, word):
        return word in self.nlps["FR"].vocab

    def process_text(self, text, nlp):
        try:
            return self.nlps[nlp](text)
        except Exception as e:
            print(e)
            return None