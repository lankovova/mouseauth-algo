import numpy as np
import pandas as pd
import string
import datasource as DS

LETTERS_UPPERCASE = list(string.ascii_uppercase)
LETTERS_LOWERCASE = list(string.ascii_lowercase)
LETTERS_AMOUNT = len(LETTERS_UPPERCASE)

LETTERS_TRANSITION_ALLOWABLE_ERROR = 0.05
GRAMMAR_ALLOWABLE_ERROR = 0.02

FULLNESS_TRAININGS_AMOUNT = 20


def getTimelineDeltas(timeline):
	timelineDeltas = []

	for index, timepoint in enumerate(timeline):
		if index + 1 < len(timeline):
			timelineDeltas.append(timeline[index + 1] - timepoint)

	return timelineDeltas


def getLetterStep(timelineDeltas):
	return max(timelineDeltas) // LETTERS_AMOUNT


def getLetter(value, step):
	letterIndex = abs(value) // step
	if value >= 0:
		return LETTERS_UPPERCASE[letterIndex if letterIndex < len(LETTERS_UPPERCASE) else -1]
	else:
		return LETTERS_LOWERCASE[letterIndex if letterIndex < len(LETTERS_LOWERCASE) else -1]


def mergeGrammars(left, right):
	return (left + right) / 2


def mergeDictOfGrammars(leftDict, rightDict):
	return { k: mergeGrammars(v, rightDict[k]) for k, v in leftDict.items() }


def getGrammarError(srcGrammar, grammarsToCheck):
	grammarLettersHits = abs(srcGrammar - grammarsToCheck) <= LETTERS_TRANSITION_ALLOWABLE_ERROR
	elementsAmount = len(srcGrammar.index) * len(srcGrammar.columns)

	return abs(elementsAmount - grammarLettersHits.sum().sum()) / elementsAmount


def isGrammarsSimilar(srcGrammars, grammarsToCheck):
	grammarsErrors = { k: getGrammarError(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	print(grammarsErrors)

	# Check if grammars errors is in OK range
	isGrammarsSimilarDict = { k: v <= GRAMMAR_ALLOWABLE_ERROR for k, v in grammarsErrors.items() }

	return True # FIXME:


def formGrammar(timeline):
	timelineDeltas = getTimelineDeltas(timeline)
	letterStep = getLetterStep(timelineDeltas)

	lettersChain = [getLetter(timepointDelta, letterStep) for timepointDelta in timelineDeltas]

	# Initialize empty matrix
	grammar = pd.DataFrame(
		np.zeros((2 * LETTERS_AMOUNT, 2 * LETTERS_AMOUNT), dtype=int),
		index=LETTERS_UPPERCASE + LETTERS_LOWERCASE,
		columns=LETTERS_UPPERCASE + LETTERS_LOWERCASE
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


def linguistic(timelines, userID):
	grammars = formGrammars(timelines)

	# Get user data
	userData = DS.getUserData(userID)

	if not userData:
		# New user
		DS.addNewUser(userID, grammars)
	elif userData["trainings"] < FULLNESS_TRAININGS_AMOUNT:
		mergedGrammars = mergeDictOfGrammars(userData["grammars"], grammars)
		DS.trainUser(userID, mergedGrammars)
	else:
		# Compare grammars
		compareResults = isGrammarsSimilar(userData["grammars"], grammars)
		return compareResults

	return True
