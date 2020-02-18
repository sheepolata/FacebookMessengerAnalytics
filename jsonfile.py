import re
from functools import partial
import json

class MessageFile(object):
	"""docstring for MessageFile"""
	def __init__(self, filepath):
		super(MessageFile, self).__init__()
		self.filepath = filepath
		
		#Fix encoding
		fix_mojibake_escapes = partial (
			re.compile(rb'\\u00([\da-f]{2})').sub,
			lambda m: bytes.fromhex(m.group(1).decode())
		)
		with open(self.filepath, 'rb') as binary_data:
			repaired = fix_mojibake_escapes(binary_data.read())
		
		#Set data
		try:
			self.data = json.loads(repaired.decode('utf8'))
		except Exception as e:
			print(e)
			self.data = {}

	def get_messages_from(self, name):
		l_my_messages = []
		for m in self.data["messages"]:
			try:
				if m["sender_name"] == name:
					l_my_messages.append(m)
			except Exception:
				print(e)
				pass

		return l_my_messages

	def get_nb_message(self):
		return len(self.data["messages"])

	def get_text_only_from(self, name):
		l = self.get_messages_from(name)
		res = []
		for d in l:
			try:
				res.append(d["content"])
			except Exception:
				pass
		return res
