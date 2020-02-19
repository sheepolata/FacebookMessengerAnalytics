
import numpy as np
import re

import os
import fnmatch
import json
from functools import partial

import nlphandler

import jsonfile

class MarkovObject(object):
    """docstring for MarkovObject"""
    def __init__(self, path_to_data):
        super(MarkovObject, self).__init__()
        self.markov_table = {}

        # self.language_word_list = {}
        # with open('data/words_alpha_en.txt') as word_file:
        #     valid_words = set(word_file.read().split())
        #     self.language_word_list["EN"] = valid_words

        # with open('data/words_alpha_fr.txt') as word_file:
        #     valid_words = set(word_file.read().split())
        #     self.language_word_list["FR"] = valid_words

        self.nlp = nlphandler.NLPHandler()

        # print("Apparement in english? {}".format(self.nlp.is_word_english("Apparement")))
        # print("Apparement in french? {}".format(self.nlp.is_word_french("Apparement")))

        # text = ("This is a sentence lol")
        # doc = self.nlp.process_text(text, "EN")

        # for token in doc:
        #     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #             token.shape_, token.is_alpha, token.is_stop)

        # print()
        # print()
        # print()

        # text = ("Ceci est une phrase en francais lol")
        # doc = self.nlp.process_text(text, "FR")

        # for token in doc:
        #     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #             token.shape_, token.is_alpha, token.is_stop)

        # t = self.nlp.process_text("Ceci est un phrase lol", "FR")
        # print(t)
        # for entity in t.ents:
        #     print(entity.text, entity.label_)

        self.END_CHAR = "__end__"

        self.ponctuation_end_sentence = ['!', '.', '?', '...']
        self.ponctuation_continue_sentence = [',', ':', '=']

        self.path_to_data = path_to_data

    def add_message_list(self, _list, sender_name):

        try:
            self.markov_table[sender_name]
        except Exception:
            self.markov_table[sender_name] = {}

        url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', re.IGNORECASE)
        for message in _list:

            #Get rid of links
            message = url_regex.sub("", message)


            #Handle ponctuation
            for p in self.ponctuation_end_sentence:
                message = message.replace(p, " "+self.END_CHAR)
                # message = message.replace(p, " "+p)
            for p in self.ponctuation_continue_sentence:
                message = message.replace(p, " "+p)

            #NLP
            split_msg = message.split()

            en = 0
            fr = 0
            for w in split_msg:
                _c = 0
                if self.nlp.is_word_french(w):
                    fr += 1
                if self.nlp.is_word_english(w):
                    en += 1
            lang = "EN" if en > fr else "FR"

            doc = self.nlp.process_text(message, lang)

            for i, word_token in enumerate(doc):
                try:
                    self.markov_table[sender_name][word_token.text]
                except Exception:

                    # Text: The original word text.
                    # Lemma: The base form of the word.
                    # POS: The simple part-of-speech tag.
                    # Tag: The detailed part-of-speech tag.
                    # Dep: Syntactic dependency, i.e. the relation between tokens.
                    # Shape: The word shape – capitalization, punctuation, digits.
                    # is alpha: Is the token an alpha character?
                    # is stop: Is the token part of a stop list, i.e. the most common words of the language?
                    
                    _data = {}
                    _data["lemma_"] = word_token.lemma_
                    _data["pos_"] = word_token.pos_
                    _data["tag_"] = word_token.tag_
                    _data["dep_"] = word_token.dep_
                    _data["shape_"] = word_token.shape_
                    _data["is_alpha"] = word_token.is_alpha
                    _data["is_stop"] = word_token.is_stop
                    self.markov_table[sender_name][word_token.text] = {"data": _data, "list":[]}

                if i >= len(split_msg)-1:
                    ok = False
                    for _d in self.markov_table[sender_name][word_token.text]["list"]:
                        if _d["word"] == self.END_CHAR:
                            _d["value"] += 1
                            ok = True
                    if not ok:
                        self.markov_table[sender_name][word_token.text]["list"].append( {"word": self.END_CHAR, "value": 1} )
                else:
                    ok = False
                    for _d in self.markov_table[sender_name][word_token.text]["list"]:
                        if _d["word"] == split_msg[i+1]:
                            _d["value"] += 1
                            ok = True
                    if not ok:
                        self.markov_table[sender_name][word_token.text]["list"].append( {"word": split_msg[i+1], "value": 1} )

            """
            #Store data
            split_msg = message.split()

            for i, word in enumerate(split_msg):
                try:
                    self.markov_table[sender_name][word]
                except Exception:
                    self.markov_table[sender_name][word] = []

                if i >= len(split_msg)-1:
                    ok = False
                    for _d in self.markov_table[sender_name][word]:
                        if _d["word"] == self.END_CHAR:
                            _d["value"] += 1
                            ok = True
                    if not ok:
                        self.markov_table[sender_name][word].append( {"word": self.END_CHAR, "value": 1} )
                else:
                    ok = False
                    for _d in self.markov_table[sender_name][word]:
                        if _d["word"] == split_msg[i+1]:
                            _d["value"] += 1
                            ok = True
                    if not ok:
                        self.markov_table[sender_name][word].append( {"word": split_msg[i+1], "value": 1} )
            """



    def load_all_data(self, save_to_file=False):
        total = len(os.listdir(self.path_to_data))
        count = 0
        print("load_all_data... {}/{} directories".format(count, total), flush=True, end='\r')


        for dir_name in os.listdir(self.path_to_data):
            complete_dir_name = self.path_to_data + dir_name + "/"
            for filename in os.listdir(complete_dir_name):
                if fnmatch.fnmatch(filename, '*.json'):
                    complete_file_path = complete_dir_name + filename
                    self.fill_all_data_from_file(complete_file_path)
            count += 1
            print("load_all_data... {}/{} directories".format(count, total), flush=True, end='\r')
            if count >= 10:
                break

        print("")
        print("load_all_data completed")
        if save_to_file:
            self.save_markovtable("./data/markovtable.json")


    def save_markovtable(self, path):
        print("Saving Markov Table to " + path)

        with open(path, 'w') as savefile:
            json.dump(self.markov_table, savefile, indent=4, sort_keys=True)

        print("Markov Table saved to " + path)

    def load_markovtable(self, path):
        print("Loading Markov Table from " + path)
        self.markov_table = json.load(open(path, 'r'))
        print("Markov Table loaded")


    def fill_all_data_from_file(self, path):
        fjson = jsonfile.MessageFile(path)


        if fjson.data == {}:
            print("No data for {}".format(path))
            return


        # print("{} : {} messages".format([f["name"] for f in fjson.data["participants"]] , fjson.get_nb_message()))
        for participant in fjson.data["participants"]:
            self.fill_named_data_from_file(fjson, participant["name"])

    def fill_named_data_from_file(self, json_file, name):
        l_my_messages_content = json_file.get_text_only_from(name)

        # markov_object.add_message_list(l_my_messages_content)
        self.add_message_list(l_my_messages_content, name)

    def generate_sentence(self, sender_name):
        if not sender_name in self.markov_table:
            return "NO " + sender_name + " IN MARKOV TABLE"

        sentence = ""

        current_word = np.random.choice(list(self.markov_table[sender_name].keys()))
        while current_word == self.END_CHAR:
            current_word = np.random.choice(list(self.markov_table[sender_name].keys()))
        sentence = current_word
        next_word = None

        while next_word != self.END_CHAR:
            #Pick a word
            next_word_list   = [wd["word"] for wd in self.markov_table[sender_name][current_word]["list"]]
            next_word_values = [wd["value"] for wd in self.markov_table[sender_name][current_word]["list"]]
            _total = sum(next_word_values)
            next_word_p = [v/_total for v in next_word_values]

            next_word = np.random.choice(next_word_list, p=next_word_p)

            #Add it
            if next_word in self.ponctuation_continue_sentence or next_word in self.ponctuation_end_sentence or next_word == self.END_CHAR:
                sentence += next_word
            else:
                sentence += " " + next_word
            current_word = next_word

        sentence = sentence.replace(self.END_CHAR, np.random.choice(self.ponctuation_end_sentence))

        return (sender_name, sentence)

    def generate_sentences(self, sender_name):
        final_sentences = ""
        _continue = True
        _p = 0.5
        while _continue:
            s = self.generate_sentence(sender_name)
            final_sentences += "\t" + s[1] + "\n"
            if np.random.rand() > _p:
                _continue = False
            else:
                _p -= 0.15
        return (sender_name, final_sentences)



    def generate_conversation(self, nb_exchange, participants):
        conversation = []

        participants_OK = (True, "None")
        for p in participants:
            if not p in self.markov_table.keys():
                participants_OK = (False, p)
                break
        if not participants_OK[0]:
            print("{} not in data...".format(participants_OK[1]))
            return []


        _sender_index = np.random.randint(0, len(participants))
        _next_sender_chance = 0.3

        for i in range(nb_exchange):
            if np.random.rand() < _next_sender_chance:
                _sender_index = (_sender_index+1) % len(participants)
            else:
                _next_sender_chance += 0.15

            _sender = participants[_sender_index]

            conversation.append(self.generate_sentences(_sender))

        return conversation


    def conversation_to_file(self, nb_exchange, participants=[], output=None, seed=-1):
        if seed != -1 and seed >= 0:
            np.random.seed(seed)
        else:
            seed = np.random.get_state()[1][0]

        if len(participants) <= 0:
            participants = list(np.random.choice(list(self.markov_table.keys()), np.random.randint(1, 2)))
            # participants.append("Antoine Gaget")

        # print(participants)

        if output == None:
            path = "./output/{}_conversation_{}.txt".format(participants, seed)
        else:
            path = output
        f = open(path, 'w')

        l = self.generate_conversation(nb_exchange, participants)

        for m in l:
            try:
                f.write("{}\n{}\n\n".format(m[0], m[1]))
            except Exception as e:
                f.write("{}\n\tERROR: {}\n\n".format(m[0], str(e)))


        f.close()

    def clear_data(self):
        self.markov_table = {}
        print("Markov Data cleared")

        
