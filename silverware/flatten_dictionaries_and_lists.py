def convert_list_to_dictionary(l):
	return {i+1: value for i, value in enumerate(l)}


def flatten_dictionaries_and_lists(x):
	"""
	:type x: list or dict
	:rtype: dict
	"""
	if isinstance(x, (list, tuple)):
		if len(x) > 1:
			x = convert_list_to_dictionary(x)
		elif len(x) == 1:
			return flatten_dictionaries_and_lists(x[0])
		else:
			return None

	if isinstance(x, dict):
		result = {}
		for key, value in x.items():
			if isinstance(value, (dict, list, tuple)):
				value = flatten_dictionaries_and_lists(value)
				if value is None:
					continue
				elif isinstance(value, dict):
					for key2, value2 in value.items():
						result[f'{key}_{key2}'] = value2
				else:
					result[key] = value
			else:
				result[key] = value
		return result
	else:
		return x
