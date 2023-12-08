import os, re, chardet
from collections import OrderedDict
from datetime import datetime


class Main:
	def __init__(self):

		self.original_filename  	= 'trans_scenario.csv'
		self.final_filename 		= f'NEW__{self.original_filename}'
		self.for_translate_filename = 'for_translate.txt'
		self.log_filename 			= 'log.txt'
		self.encoding 				= None

		self.ignored_lines = ['#', '＃', 'DO NOT EDIT', 'ver1.00', '>mn	_EnemyName_+']
		self.ignored_sings 	= [
			'・・・・・・・・・・・・	…………',
			'･････････	………',
			'・・・・・・・・・	………',
			'･･････	……',
			'・・・・・・	……',
			'･････	……',
			'・・・	…',
			'・	…',
			'･	…',

			'･･････！',
			'！？	!?',
			'？', '！', 
			'（？？）',
			'？	?', 
			'！	!',
			'？', 

			'１・１・０',

			'（･･････）',
			'････････････',
			'・・・・・・・・・・・・',
			'･･･････',
			'･･････',
			'･････',
			'･･･',
			'・',
		]

		# (кандзи, хирагану, катакану)
		self.JA_ONLY = re.compile(r'^[\u3000-\u303F\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\s]+$')
		self.JA 	 = re.compile(r'[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF]') 
		self.RU 	 = re.compile(r'[\u0400-\u04FF]')
		self.EN 	 = re.compile(r'[a-zA-Z]')

		self.start()

		
	def read_file(self):

		if os.path.exists(self.original_filename) and os.path.splitext(self.original_filename)[1] == '.csv':
			try:
				with open(self.original_filename, 'rb') as f:
					raw_data = f.read()

				self.encoding = chardet.detect(raw_data)['encoding']

				with open(self.original_filename, 'r', encoding=self.encoding) as f:
					return f.readlines()

			except Exception as e:
				self.log(f'ERROR! read data from "{self.original_filename}"\n\t{e}')
				return []
		else:
			self.log(f'ERROR! file missing "{self.original_filename}"')
			return []

	def start(self):

		original = self.read_file()
		
		if original:
			lines = [i for i in original if re.search(self.JA, i) and not re.search(self.EN, i)]
			lines = [i for i in lines if i.strip() not in self.ignored_sings]
			lines = [i for i in lines if all(k not in i for k in self.ignored_lines)]
			lines = OrderedDict((l.rstrip(), None) for l in lines)
			tr_lines = [f'{l}\n' for l in lines]

			lines 	 = sorted(lines)
			tr_lines = sorted(tr_lines)

			if not os.path.exists(self.for_translate_filename):
				try:
					with open(self.for_translate_filename, 'w', encoding='utf-8') as f:
						f.writelines(tr_lines)
				except Exception as e:
					self.log(f'ERROR! Cannot write data to "{self.for_translate_filename}"\n\t{e}')


			try:
				with open(self.for_translate_filename, 'r', encoding='utf-8') as f:
					tr_lines = f.readlines()
			except Exception as e:
				self.log(f'ERROR! Cannot read data from "{self.for_translate_filename}"\n\t{e}')

			ja_tr_dict = {}

			for ja, tr in zip(lines, tr_lines):
				# Избегать дублирование ja строки при отсутствии перевода
				ja_tr_dict[ja] = tr.strip() if ja.strip() != tr.strip() else None

			lines_amount = {}
			try:
				with open(self.final_filename, 'w', encoding=self.encoding) as f:

					unique_tr, unique_not_tr = set(), set()
					tr, not_tr	= 0, 0

					for line in original:
						line = line.rstrip()
						if line in ja_tr_dict and ja_tr_dict[line] is not None:
							new_line = f'{line}\t{ja_tr_dict[line]}\n'
							f.write(new_line)
							unique_tr.add(new_line)
							tr += 1
						else:
							f.write(f'{line}\n')
							unique_not_tr.add(line)
							not_tr += 1
					lines_amount['tr']    			= tr
					lines_amount['not_tr'] 			= not_tr
					lines_amount['unique_tr'] 		= len(unique_tr)
					lines_amount['unique_not_tr'] 	= len(unique_not_tr)
					self.log(lines_amount)

			except Exception as e:
				self.log(f'ERROR! Cannot write data to "{self.final_filename}"\n\t{e}')


	def log(self, msg=None):

		time = datetime.now()
		time = time.strftime('%Y-%m-%d %H:%M:%S.%f')

		if msg is not None:
			with open(self.log_filename, 'a', encoding='utf-8') as f:
				if isinstance(msg, dict):
					f.write(f'{time}\n')
					f.write(f'\t{msg["tr"]} --- lines translated\n')
					f.write(f'\t{msg["not_tr"]} --- lines NOT translated\n')
					f.write(f'\t{msg["unique_tr"]} --- unique strings translated\n')
					f.write(f'\t{msg["unique_not_tr"]} --- unique strings NOT translated\n')
				if isinstance(msg, str):
					f.write(f'{time}: {msg}\n')

				f.write('\n')


if __name__ == '__main__':
	main = Main()
