# This file is a part of:
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██
#__________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
#‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


import re, math, operator

def readncf(text):
	groups = re.findall(r"((?:1|2|4|8|16|32)\.?)(?:(#?[a-g])([1-3])|-)", text)

	notes = []
	tick = 0
	for tup in groups:
		dur = tup[0]
		if dur[-1] == '.': dur = 4 / int(dur[:-1]) * 1.5
		else: dur = 4 / int(dur)
		if bool(tup[1]): key = 27 + notes.index(tup[1]) + 12*(int(tup[2])-1)
		else: key = None
		if key is not None and dur >= 0.25: notes.append({'tick':tick, 'layer': 0, 'inst':0, 'key':key, 'isPerc': False, 'duration': dur*4})
		tick += dur*4

	headers = {}
	headers['file_version'] = 3
	headers['vani_inst'] = 16
	headers['length'] = 0
	headers['height'] = 1
	headers['name'] = ''
	headers['author'] = ''
	headers['orig_author'] = ''
	headers['description'] = ''
	headers['tempo'] = 100
	headers['auto-saving'] = False
	headers['auto-saving_time'] = 10
	headers['time_sign'] = 4
	headers['minutes_spent'] = 0
	headers['left_clicks'] = 0
	headers['right_clicks'] = 0
	headers['block_added'] = 0
	headers['block_removed'] = 0
	headers['import_name'] = ''
	headers['inst_count'] = 0

	layers = []
	customInsts = []
	usedInsts = []

	a = 1

	sortedNotes = sorted(notes, key = operator.itemgetter('tick', 'layer') )
	return {'headers':headers, 'notes':sortedNotes, 'layers':layers, 'customInsts':customInsts, 'IsOldVersion':False, 'hasPerc':False, 'maxLayer':0, 'usedInsts':usedInsts}

def writencf(data):
	tunes = ["c", "#c", "d", "#d", "e", "f", "#f", "g", "#g", "a", "#a", "b"]

	print(data['notes'][0])

	out = []
	for note in data['notes']:
		ele = ''
		ext = ['']
		idur = dur = note['duration'] / 4
		while dur > 4 and dur - 4 >= 4:
			ext.append("1-")
			dur -= 4
		if dur > 0:
			sub = 1
			c = 0
			while dur >= 0.125 and sub > 0:
				sub = 2**(int(math.log(dur*8, 2))-3)
				subi = int(4 / sub)# if idur > 4 else sub
				if c == 0:
					if idur > 4:
						ele = '1' + ele
					else:
						ele = str(subi) + ele
				else:
					ext.append(f'{subi}-')
				dur -= sub
				c += 1

		key = note['key'] - 27

		ele += f'{tunes[key%12]}{key//12 + 1}' + ' '.join(ext)

		out.append(ele)

	out = ' '.join(out)

	return out