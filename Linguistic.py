import numpy as np
import pandas as pd
import datasource as DS
import constants as c
import math

def getTimelineDeltas(timeline):
	timelineDeltas = []

	for index, timepoint in enumerate(timeline):
		if index + 1 < len(timeline):
			timelineDeltas.append(timeline[index + 1] - timepoint)

	return timelineDeltas


def getLetter(value, step):
	letterIndex = abs(value) // step
	if value >= 0:
		return c.LETTERS_UPPERCASE[letterIndex if letterIndex < len(c.LETTERS_UPPERCASE) else -1]
	else:
		return c.LETTERS_LOWERCASE[letterIndex if letterIndex < len(c.LETTERS_LOWERCASE) else -1]


def formGrammar(timeline):
	timelineDeltas = getTimelineDeltas(timeline)
	letterStep = math.ceil(max(timelineDeltas) / c.LETTERS_AMOUNT)

	lettersChain = [getLetter(timepointDelta, letterStep) for timepointDelta in timelineDeltas]

	# Initialize empty matrix
	grammar = pd.DataFrame(
		np.zeros((2 * c.LETTERS_AMOUNT, 2 * c.LETTERS_AMOUNT), dtype=int),
		index=c.LETTERS_UPPERCASE + c.LETTERS_LOWERCASE,
		columns=c.LETTERS_UPPERCASE + c.LETTERS_LOWERCASE
	)

	# Add transitions between letters amount
	previousLetter = None
	for letter in lettersChain:
		if previousLetter:
			grammar.at[previousLetter, letter] += 1
		previousLetter = letter

	# Convert transitions amount into transition chance percentage
	return grammar.apply(lambda x: x / x.sum() if x.any() else x, axis=1)


def formGrammars(timelines):
	return { k: formGrammar(v) for k, v in timelines.items() }


def mergeGrammars(left, right):
	return (left + right) / 2


def mergeDictOfGrammars(leftDict, rightDict):
	return { k: mergeGrammars(v, rightDict[k]) for k, v in leftDict.items() }


def getGrammarError(srcGrammar, grammarsToCheck):
	grammarLettersHits = abs(srcGrammar - grammarsToCheck) <= c.LETTERS_TRANSITION_ALLOWABLE_ERROR
	elementsAmount = len(srcGrammar.index) * len(srcGrammar.columns)

	return abs(elementsAmount - grammarLettersHits.sum().sum()) / elementsAmount


def isGrammarsSimilar(srcGrammars, grammarsToCheck):
	grammarsErrors = { k: getGrammarError(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	print('old', grammarsErrors)

	# Check if grammars errors is in OK range
	isGrammarsSimilarDict = { k: v <= c.GRAMMAR_ALLOWABLE_ERROR for k, v in grammarsErrors.items() }

	return True # FIXME:


# TODO
def TODO_getGrammarAbsoluteError(srcGrammar, grammarToCheck):
	diffGrammar = abs(grammarToCheck - srcGrammar)
	return diffGrammar.values.sum() / (2 * len(diffGrammar.index) * len(diffGrammar.index))


# TODO
def TODO_getGrammarsAbsoluteError(srcGrammars, grammarsToCheck):
	grammarsSimilarity = { k: TODO_getGrammarAbsoluteError(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	print('new', grammarsSimilarity)
	pass


def linguistic(timelines, userID):
	currentGrammars = formGrammars(timelines)

	# Get user data
	userSourceData = DS.getUserData(userID)

	if userSourceData is None:
		# New user
		DS.addNewUser(userID, currentGrammars)
	elif userSourceData["trainings"] < c.FULLNESS_TRAININGS_AMOUNT:
		mergedGrammars = mergeDictOfGrammars(userSourceData["grammars"], currentGrammars)
		DS.trainUser(userID, mergedGrammars)
	else:
		# Compare grammars
		TODO_getGrammarsAbsoluteError(userSourceData["grammars"], currentGrammars)
		return isGrammarsSimilar(userSourceData["grammars"], currentGrammars)

	return True
