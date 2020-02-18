
#INSTALL

*Python3.7.6* used for dev.

Use requirements.txt to install required libraries.

Download en_core_web_lg and fr_core_news_md from the [Spacy Website](https://spacy.io/models) **UNUSED FOR NOW - WIP**

#USAGE

Go to Facebook and ask for downloading your messager data. The zip should contain a *inbox* folder.
Use this folder to load your data.

Use python *./main.py -h* for help using the program

`Usage: python ./main.py [options]`

`options list:`

`    -path       Path to the inbox where messages are stored (default:C:/Users/antoi/Documents/facebook-antoinegaget_messages/messages/inbox/)`

`    -rlm        If True, reload the markov chain from the inbox. If False, use data/markovtable.json (default:False)`

`    -part       Participant name as a String list (e.g. "Name1, Name2 Surname2") (default:[])`

`    -out        Output file name, where output will be saved. If not specified, name auto generated (default:None)`

`    -s  Size of the conversation to be generated, in number of message (default:500)`
