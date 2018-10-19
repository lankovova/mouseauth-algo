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


def getMovementLetter(value, step):
	letterIndex = abs(value) // step
	if value >= 0:
		return LETTERS_UPPERCASE[letterIndex if letterIndex < len(LETTERS_UPPERCASE) else -1]
	else:
		return LETTERS_LOWERCASE[letterIndex if letterIndex < len(LETTERS_LOWERCASE) else -1]


def mergeGrammars(left, right):
	return (left + right) / 2


def isSimilar(srcGrammar, toCheckGrammar):
	grammarLettersHits = abs(srcGrammar - toCheckGrammar) <= LETTERS_TRANSITION_ALLOWABLE_ERROR
	elementsAmount = len(srcGrammar.index) * len(srcGrammar.columns)

	grammarError = abs(elementsAmount - grammarLettersHits.sum().sum()) / elementsAmount

	print(grammarError) # FIXME:

	return grammarError <= GRAMMAR_ALLOWABLE_ERROR


def formGrammar(timeline):
	timelineDeltas = getTimelineDeltas(timeline)
	letterStep = getLetterStep(timelineDeltas)

	lettersChain = [getMovementLetter(timepointDelta, letterStep) for timepointDelta in timelineDeltas]

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


def linguistic(timelines, userID):
	# Generate grammars
	mxGrammar = formGrammar(timelines["mX"])

	# Get user data
	userData = DS.getUserData(userID)

	if not userData:
		# New user
		DS.addNewUser(userID, { "mX": mxGrammar.to_json() })
	elif userData["trainings"] < FULLNESS_TRAININGS_AMOUNT:
		# Train
		srcMxGrammar = pd.read_json(userData["grammars"]["mX"])
		updatedMxGrammar = mergeGrammars(srcMxGrammar, mxGrammar)

		DS.trainUser(userID, { "mX": updatedMxGrammar.to_json() })
	else:
		# Compare grammars
		srcMxGrammar = pd.read_json(userData["grammars"]["mX"])
		return isSimilar(srcMxGrammar, mxGrammar)

	return True
