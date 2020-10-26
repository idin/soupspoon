CAPITALIZATION_EXCEPTIONS = ["and", "or", "the", "a", "of", "in"]
PUNCTUATIONS = [".", "?", "!"]


def get_num_capitalized(words):
	if isinstance(words, str):
		words =  [word for word in words.split() if word not in CAPITALIZATION_EXCEPTIONS]

	return sum([1 for word in words if word[0].isupper()])


def is_body_text(text):
	if not isinstance(text, str):
		return False

	# if there are very few words it's not proper
	words = [word for word in text.split() if word not in CAPITALIZATION_EXCEPTIONS]
	if len(words) < 4:
		return False

	# if there are more than two punctuations it's a body text if there is zero, it is not
	num_punctuations = 0
	if any([True for p in PUNCTUATIONS if text.endswith(p)]):
		num_punctuations += 1

	for p in PUNCTUATIONS:
		for p_suffix in ['\n', ' ']:
			num_punctuations += text.count(f'{p}{p_suffix}')

	if num_punctuations == 0:
		return False
	elif num_punctuations > 1:
		return True

	# if there are too many short words it's not a text
	num_short_words = sum([1 for word in words if len(word)<4])
	if num_short_words > len(words) / 2 - 1:
		return False

	# if almost all words are capitalized it is not body text
	num_capitalized = get_num_capitalized(words=words)

	# allow one mistake
	if num_capitalized >= len(words) - 1:
		return False

	return True
