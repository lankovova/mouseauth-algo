import numpy as np
import pandas as pd
import datasource as DS
import constants as c
import math
import utils

def getTimelineDeltas(timeline):
	timelineDeltas = []

	for index, timepoint in enumerate(timeline):
		if index + 1 < len(timeline):
			timelineDeltas.append(timeline[index + 1] - timepoint)

	return timelineDeltas

def getLinguisticRule(timeline):
	timelineDeltas = getTimelineDeltas(timeline)
	sortedTimelineDeltas = sorted(timelineDeltas)
	minDelta = abs(sortedTimelineDeltas[0])
	maxDelta = sortedTimelineDeltas[-1]

	negativeIntervalLength = math.ceil(minDelta / (c.LETTERS_AMOUNT - 1))
	positiveIntervalLength = math.ceil(maxDelta / (c.LETTERS_AMOUNT - 1))

	return {
		'negativeIntervalLength': negativeIntervalLength,
		'positiveIntervalLength': positiveIntervalLength,
	}

def getLinguisticRules(timelines):
	return { k: getLinguisticRule(v) for k, v in timelines.items() }

def mergeRule(prevRule, currentRule):
	return { k: round((v + currentRule[k]) / 2) for k, v in prevRule.items() }

def mergeRules(prevRules, currentRules):
	return { k: mergeRule(v, currentRules[k]) for k, v in prevRules.items() }

def getLetter(value, rule):
	if value == 0:
		return 'null'
	elif value > 0:
		letterIndex = (value - 1) // rule['positiveIntervalLength']
		return c.LETTERS_UPPERCASE[letterIndex if letterIndex < len(c.LETTERS_UPPERCASE) else -1]
	else:
		letterIndex = (abs(value) - 1) // rule['negativeIntervalLength']
		return c.LETTERS_LOWERCASE[letterIndex if letterIndex < len(c.LETTERS_LOWERCASE) else -1]

def formGrammar(timeline, rule):
	timelineDeltas = getTimelineDeltas(timeline)

	lettersChain = [getLetter(timepointDelta, rule) for timepointDelta in timelineDeltas]

	print(' '.join(lettersChain))
	print('============================================')

	# Initialize empty matrix
	grammar = pd.DataFrame(
		np.zeros((len(c.TRANSITION_MATRIX_INDEXES), len(c.TRANSITION_MATRIX_INDEXES)), dtype=int),
		index=c.TRANSITION_MATRIX_INDEXES,
		columns=c.TRANSITION_MATRIX_INDEXES
	)

	# Add transitions between letters amount
	previousLetter = None
	for letter in lettersChain:
		if previousLetter:
			grammar.at[previousLetter, letter] += 1
		previousLetter = letter

	# Convert transitions amount into transition chance percentage
	return grammar.apply(lambda x: x / x.sum() if x.any() else x, axis=1)

def formGrammars(timelines, rules):
	return { k: formGrammar(v, rules[k]) for k, v in timelines.items() }

def mergeGrammars(left, right):
	summedUp = left + right
	return summedUp.apply(lambda x: x / 2 if x.sum() > 1 else x, axis=1)

def mergeDictOfGrammars(leftDict, rightDict):
	return { k: mergeGrammars(v, rightDict[k]) for k, v in leftDict.items() }

def getGrammarError(srcGrammar, grammarsToCheck):
	grammarLettersHits = abs(srcGrammar - grammarsToCheck) <= c.LETTERS_TRANSITION_ALLOWABLE_ERROR
	elementsAmount = len(srcGrammar.index) * len(srcGrammar.columns)

	return abs(elementsAmount - grammarLettersHits.sum().sum()) / elementsAmount

def isGrammarsSimilar(srcGrammars, grammarsToCheck):
	grammarsErrors = { k: getGrammarError(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	utils.printDictInPercents('mine grammarsError', grammarsErrors)

	# Check if grammars errors is in OK range
	isGrammarsSimilarDict = { k: v <= c.GRAMMAR_ALLOWABLE_ERROR for k, v in grammarsErrors.items() }

	return True # FIXME

# TODO
def TODO_getGrammarAbsoluteError(srcGrammar, grammarToCheck):
	diffGrammar = abs(grammarToCheck - srcGrammar)
	return diffGrammar.values.sum() / (2 * len(diffGrammar.index))

# TODO
def TODO_getGrammarsAbsoluteError(srcGrammars, grammarsToCheck):
	grammarsSimilarity = { k: TODO_getGrammarAbsoluteError(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	utils.printDictInPercents('grammarsAbsoluteError', grammarsSimilarity)
	pass

def TODO_zerosGrammarComparison(srcGrammar, grammarToCheck):
	summedUp = srcGrammar + grammarToCheck
	zeroesInSimilarPositionsAmount = (summedUp == 0).sum(axis=1).sum()
	similarityIndex = zeroesInSimilarPositionsAmount / (len(srcGrammar.index) * len(srcGrammar.index))
	return similarityIndex

def TODO_zerosGrammarsComparison(srcGrammars, grammarsToCheck):
	zerosAndOncesSimilarity = { k: TODO_zerosGrammarComparison(v, grammarsToCheck[k]) for k, v in srcGrammars.items() }
	utils.printDictInPercents('zerosAndOncesSimilarity', zerosAndOncesSimilarity)

def linguistic(timelines, userID):
	# Get user data
	userSourceData = DS.getUserData(userID)

	if userSourceData is None:
		# New user
		rules = getLinguisticRules(timelines)
		initialGrammars = formGrammars(timelines, rules)

		DS.addNewUser(userID, initialGrammars, rules)
		return { "code": "training" }

	if userSourceData["trainings"] < c.FULLNESS_TRAININGS_AMOUNT:
		currentRules = getLinguisticRules(timelines)
		mergedRules = mergeRules(userSourceData["rules"], currentRules)

		currentGrammars = formGrammars(timelines, mergedRules)
		mergedGrammars = mergeDictOfGrammars(userSourceData["grammars"], currentGrammars)

		DS.trainUser(userID, mergedGrammars, mergedRules)
		return { "code": "training" }

	# Compare grammars
	# FIXME: Compare two error algos
	currentGrammars = formGrammars(timelines, userSourceData["rules"])

	print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
	utils.printGrammar(userSourceData["grammars"])
	utils.printGrammar(currentGrammars)

	TODO_getGrammarsAbsoluteError(userSourceData["grammars"], currentGrammars)
	isGrammarsSimilar(userSourceData["grammars"], currentGrammars)
	TODO_zerosGrammarsComparison(userSourceData["grammars"], currentGrammars)

	return { "code": "ok" }
	# return { "code": "bad" }
