import string

# LETTERS_UPPERCASE = list(string.ascii_uppercase)
# LETTERS_LOWERCASE = list(string.ascii_lowercase)
LETTERS_UPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'Z']
LETTERS_LOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'z']
LETTERS_AMOUNT = len(LETTERS_UPPERCASE)

TRANSITION_MATRIX_INDEXES = list(reversed(LETTERS_LOWERCASE)) + ['null'] + LETTERS_UPPERCASE

LETTERS_TRANSITION_ALLOWABLE_ERROR = 0.05
GRAMMAR_ALLOWABLE_ERROR = 0.02

FULLNESS_TRAININGS_AMOUNT = 20
