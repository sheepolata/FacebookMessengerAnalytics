from datetime import datetime
import sys

import jsonfile
import markovchain


def main():

	args = [
		(
			'path',
			'path_to_data',
			"C:/Users/antoi/Documents/facebook-antoinegaget_messages/messages/inbox/",
			'Path to the inbox where messages are stored',
			False,
			False
		),
		(
			'rlm',
			'reload_markov',
			False,
			'If True, reload the markov chain from the inbox. If False, use data/markovtable.json',
			True,
			False
		),
		(
			'part',
			'participants',
			[],
			'Participant name as a String list (e.g. \"Name1, Name2 Surname2\")',
			False,
			True
		),
		(
			'out',
			'output_file',
			None,
			'Output file name, where output will be saved. If not specified, name auto generated',
			False,
			False
		),
		(
			's',
			'size',
			500,
			'Size of the conversation to be generated, in number of message',
			False, 
			False
		)
	]

	if '--help' in sys.argv or '-h' in sys.argv:
		print('Usage: python {} [options]'.format(sys.argv[0]))
		print('options list:')
		for name_, _, default_value, help_message, no_value, _ in args:
			print('    -{}\t{} (default:{})'.format(name_, help_message, default_value))

		print()
	else:
		option_values = {}
		
		for name_, fullname, default_value, help_message, no_value, is_array in args:
			try:
				if not no_value:
					id_name = sys.argv.index('-{}'.format(name_)) + 1
					param_value = sys.argv[id_name]
					if param_value.isdigit():
						param_value = int(param_value)
					elif param_value == 'True':
						param_value = True
					elif param_value == 'False':
						param_value = False
					elif is_array:
						param_value = param_value.split(',')
						param_value = [s.strip() for s in param_value]

					option_values[fullname] = param_value
				else:
					id_name = sys.argv.index('-{}'.format(name_))
					option_values[fullname] = not default_value
			except:
				option_values[fullname] = default_value

		# print(option_values)

		markov_object = markovchain.MarkovObject(option_values["path_to_data"])

		if option_values["reload_markov"]:
			markov_object.load_all_data(save_to_file=True)
		else:
			markov_object.load_markovtable("./data/markovtable.json")

			markov_object.conversation_to_file(option_values["size"], participants=option_values["participants"], output=option_values["output_file"])

		print("Done")	


if __name__ == '__main__':
	main()