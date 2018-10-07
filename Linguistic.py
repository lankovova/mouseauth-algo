import numpy as np
import pandas as pd
import string

LETTERS_UPPERCASE = list(string.ascii_uppercase)
LETTERS_LOWERCASE = list(string.ascii_lowercase)
LETTERS_AMOUNT = len(LETTERS_UPPERCASE)

MAX_MOVEMENT_VALUE = 500
MOVEMENT_STEP = MAX_MOVEMENT_VALUE // LETTERS_AMOUNT

def getMovementLetter(value):
	letterIndex = abs(value) // MOVEMENT_STEP

	if value >= 0:
		return LETTERS_UPPERCASE[letterIndex if letterIndex < len(LETTERS_UPPERCASE) else -1]
	else:
		return LETTERS_LOWERCASE[letterIndex if letterIndex < len(LETTERS_LOWERCASE) else -1]

def linguistic(timeline):
	# Get letters timelines
	movementXLettersList = [getMovementLetter(timepoint["mX"]) for timepoint in timeline]
	# movementYLettersList = [getMovementLetter(timepoint["mY"]) for timepoint in timeline]

	# Initialize empty matrix
	transitionsPD = pd.DataFrame(
		np.zeros((2 * LETTERS_AMOUNT, 2 * LETTERS_AMOUNT), dtype=int),
		index=LETTERS_UPPERCASE+LETTERS_LOWERCASE,
		columns=LETTERS_UPPERCASE+LETTERS_LOWERCASE
	)

	# Add transitions between letters amount
	previousLetter = None
	for letter in movementXLettersList:
		if previousLetter:
			transitionsPD.at[previousLetter, letter] += 1
		previousLetter = letter

	# TODO: Convert transitions amount into transition chance percentage


	print(transitionsPD.head())

	return { "transitions": transitionsPD.reset_index().to_json(orient="records") }
