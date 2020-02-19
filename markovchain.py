
import numpy as np
import re

import os
import fnmatch
import json
from functools import partial
import time 

import nlphandler
import utils
import jsonfile

class MarkovObject(object):
    """docstring for MarkovObject"""
    def __init__(self, path_to_data):
        super(MarkovObject, self).__init__()
        self.markov_table = {}

        self.nlp = None

        # self.language_word_list = {}
        # with open('data/words_alpha_en.txt') as word_file:
        #     valid_words = set(word_file.read().split())
        #     self.language_word_list["EN"] = valid_words

        # with open('data/words_alpha_fr.txt') as word_file:
        #     valid_words = set(word_file.read().split())
        #     self.language_word_list["FR"] = valid_words

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
        self.old_school_smileys = ['=)', '=D', ':)', ':p', ':(', ':\'(', ';)', 'xD', 'xd', 'XD', '^^']

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
            # for p in self.ponctuation_end_sentence:
            #     message = message.replace(p, " "+p)
            #     # message = message.replace(p, " "+p)
            # for p in self.ponctuation_continue_sentence:
            #     message = message.replace(p, " "+p)

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

                # if i >= len(doc)-1:
                #     ok = False
                #     for _d in self.markov_table[sender_name][word_token.text]["list"]:
                #         if _d["word"] == self.END_CHAR:
                #             _d["value"] += 1
                #             ok = True
                #     if not ok:
                #         self.markov_table[sender_name][word_token.text]["list"].append( {"word": self.END_CHAR, "value": 1} )
                # else:
                if i < (len(doc) - 1):
                    ok = False
                    for _d in self.markov_table[sender_name][word_token.text]["list"]:
                        if _d["word"] == doc[i+1].text:
                            _d["value"] += 1
                            ok = True
                    if not ok:
                        self.markov_table[sender_name][word_token.text]["list"].append( {"word": doc[i+1].text, "value": 1} )

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

    def load_nlp(self):
        if self.nlp == None:
            self.nlp = nlphandler.NLPHandler()

    def load_all_data(self, save_to_file=False):
        self.load_nlp()

        total = len(os.listdir(self.path_to_data))
        count = 0
        l_time = []
        # print("load_all_data... {}/{} directories".format(count, total), flush=True, end='\r')


        def _print_load():
            if len(l_time) <= 0:
                return
            mean_t = np.mean(l_time)
            total_remaining = int(round(mean_t * (total-count)))
            if total_remaining <= 120:
                total_remaining_str = str(total_remaining) + 's'
            else:
                total_remaining_str = "{}m{}s".format(int(round(total_remaining/60.0)), int(total_remaining%60))
            to_print = "load_all_data... {}/{} directories -- ETA {}".format(count, total, total_remaining_str)
            if len(to_print) <= 51:
                to_print += "          "
            print(to_print, flush=True, end='\r')

        loading_display_timer = utils.perpetualTimer(0.2, _print_load)
        loading_display_timer.start()

        for dir_name in os.listdir(self.path_to_data):
            t = time.time()
            complete_dir_name = self.path_to_data + dir_name + "/"
            for filename in os.listdir(complete_dir_name):
                if fnmatch.fnmatch(filename, '*.json'):
                    complete_file_path = complete_dir_name + filename
                    self.fill_all_data_from_file(complete_file_path)
            count += 1
            t = time.time() - t
            l_time.append(t)
            # if len(l_time) > 10:
            #     l_time = l_time[1:]
            # print("load_all_data... {}/{} directories".format(count, total), flush=True, end='\r')

        loading_display_timer.cancel()

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

    def get_pronoun_list(self, sender_name):
        all_words = list(self.markov_table[sender_name].keys())

        pronouns = [w for w in all_words if self.markov_table[sender_name][w]["data"]["pos_"] in ["PRON", "DET"]]

        return pronouns

    def generate_sentence(self, sender_name):
        if not sender_name in self.markov_table:
            return "NO " + sender_name + " IN MARKOV TABLE"

        sentence = ""

        if len(self.get_pronoun_list(sender_name)) <= 0:
            return "{} HAS NO PRONOUNS IN HIS LIST...".format(sender_name)

        current_word = np.random.choice(self.get_pronoun_list(sender_name))
        while current_word in self.ponctuation_end_sentence+self.ponctuation_continue_sentence:
            current_word = np.random.choice(self.get_pronoun_list(sender_name))
        sentence = current_word
        next_word = None

        counter = 0
        counter_max = 100
        # while next_word != self.END_CHAR:
        while not next_word in self.ponctuation_end_sentence+self.old_school_smileys:
            if counter > counter_max:
                sentence += " (END BECAUSE TOO LONG)"
                break
            #Pick a word
            try:
                next_word_list   = [wd["word"] for wd in self.markov_table[sender_name][current_word]["list"]]
            except Exception:
                current_word = np.random.choice(list(self.markov_table[sender_name].keys()))
                next_word_list   = [wd["word"] for wd in self.markov_table[sender_name][current_word]["list"]]

            if len(next_word_list) <= 0:
                break

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
            counter += 1

            # print(sentence)
            # time.sleep(0.3)

        #sentence = sentence.replace(self.END_CHAR, "")#np.random.choice(self.ponctuation_end_sentence))

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

        participants_OK = (True, "None")
        for p in participants:
            if not p in self.markov_table.keys():
                participants_OK = (False, p)
                break
        if not participants_OK[0]:
            print("{} not in data...".format(participants_OK[1]))
            return {}

        conversation = {"conversation": [], "participants": participants}

        _sender_index = np.random.randint(0, len(participants))
        _next_sender_chance = 0.3

        print("Generating conversation... {}/{}".format(0, nb_exchange), flush=True, end='\r')

        for i in range(nb_exchange):
            if np.random.rand() < _next_sender_chance:
                _sender_index = (_sender_index+1) % len(participants)
            else:
                _next_sender_chance += 0.15

            _sender = participants[_sender_index]
            sentences = self.generate_sentences(_sender)
            _d = {}
            _d["sender_name"] = sentences[0]
            _d["content"]     = sentences[1]
            _d["timestamp"]   = i

            conversation["conversation"].append(_d)
            print("Generating conversation... {}/{}".format(i, nb_exchange), flush=True, end='\r')

        print("Generating conversation... {}/{}... Done!".format(i, nb_exchange))
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
            path = "./output/{}_conversation_{}.json".format(participants, seed)
        else:
            path = output
        f = open(path, 'w')

        l = self.generate_conversation(nb_exchange, participants)


        f.write(json.dumps(l, indent=4, sort_keys=True))
        # json.dumps(f, l)

        # for m in l:
        #     try:
        #         f.write("{}\n{}\n\n".format(m[0], m[1]))
        #     except Exception as e:
        #         f.write("{} (ERRORED MESSAGE {})\n{}\n\n".format(m[0], e, m[1].encode('latin-1').decode('utf-8')))


        f.close()

    def clear_data(self):
        self.markov_table = {}
        print("Markov Data cleared")

        
