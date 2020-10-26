def has_bullet(string):
	if not isinstance(string, str):
		return False

	string = string.strip()

	if len(string) < 2:
		return False

	# if it is of type:
	# 	- bullet point
	# 	a bullet point
	# 	1 bullet point
	# split by space
	split_by_space = string.split()
	if len(split_by_space) > 1 and len(split_by_space[0]) == 1 and split_by_space[1][0].isalpha():
		return True

	# if it is of type:
	# 	-bullet point
	# 	*bullet point
	if not string[0].isalpha() and not string[0].isnumeric() and string[1].isalpha():
		return True

	return False


def is_bullet_heading(string):
	if not isinstance(string, str):
		return False

	string = string.strip()

	if len(string) < 2:
		return False

	if string[-1] in [':', '?']:
		return True

	return False


def is_bullet_point(text, previous_text):
	if not isinstance(text, str) or not isinstance(previous_text, str):
		return False

	text = text.strip()
	previous_text = previous_text.strip()

	if len(text) < 2 or len(previous_text) < 2:
		return False

	if is_bullet_heading(previous_text) and has_bullet(text):
		return True

	if has_bullet(previous_text) and has_bullet(text):
		return True

	return False
