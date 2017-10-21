import re

arrival = {'пришёл', 'пришел', 'пришла', 'добрался', 'добралась', 'работе', 'месте', 'привет' }
departure = {'ушёл', 'ушел', 'ушла', 'пока', 'свидания', 'свиданья'}

def analyze(text):
	text = text.lower()
	words = text.split(' ')
	for w in words:
		if w in arrival:
			return 'arrival'
		if w in departure:
			return 'departure'
		if re.findall(r'статистик', w):
			return 'stat'
		