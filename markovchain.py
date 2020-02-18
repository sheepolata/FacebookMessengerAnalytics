
import numpy as np
import re

import os
import fnmatch
import json
from functools import partial

import spacy

import jsonfile

class MarkovObject(object):
    """docstring for MarkovObject"""
    def __init__(self, path_to_data):
        super(MarkovObject, self).__init__()
        self.markov_table = {}

        self.language_word_list = {}
        with open('data/words_alpha_en.txt') as word_file:
            valid_words = set(word_file.read().split())
            self.language_word_list["EN"] = valid_words

        with open('data/words_alpha_fr.txt') as word_file:
            valid_words = set(word_file.read().split())
            self.language_word_list["FR"] = valid_words

        print("Loading Spacy en_core_web_lg...", flush=True, end='\r')
        self.nlp_en = spacy.load("en_core_web_lg")
        print("Loading Spacy en_core_web_lg... Done!")

        print("Loading Spacy fr_core_news_md...", flush=True, end='\r')
        self.nlp_fr = spacy.load("fr_core_news_md")
        print("Loading Spacy fr_core_news_md... Done!")

        # print("Apparement in english? {}".format("Apparement" in self.nlp_en.vocab))
        # print("Apparement in french? {}".format("Apparement" in self.nlp_fr.vocab))

        test = self.nlp_fr("Apparement je suis allez a la maison en voiture.")
        for entity in test.ents:
            print(entity.text, entity.label_)

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
            next_word_list   = [wd["word"] for wd in self.markov_table[sender_name][current_word]]
            next_word_values = [wd["value"] for wd in self.markov_table[sender_name][current_word]]
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
            participants.append("Antoine Gaget")

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

        
