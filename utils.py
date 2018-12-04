def printGrammar(grammars, grammarKey='mX'):
	print('=============== ' + grammarKey + ' ===============')
	print(grammars[grammarKey])

def printDictInPercents(title, myDict):
	print('================= ' + title + ' =================')
	print({ k: str(round(v * 100, 2)) + '%' for k, v in myDict.items() })
