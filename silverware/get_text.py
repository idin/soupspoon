from bs4 import BeautifulSoup, Tag, NavigableString
from slytherin.collections import flatten as flatten_list


def get_text(tags, sep=' ', flatten=False):
	"""
	:type tags: list[list] or list[BeautifulSoup] or list[Tag] or list[NavigableString] or BeautifulSoup or Tag or NavigableString
	:type sep: str
	:return:
	"""

	if not isinstance(tags, (tuple, list)):
		if not (hasattr(tags, 'children') and tags.children):
			if hasattr(tags, 'text'):
				result = (tags.text).strip()
			else:
				result = str(tags).strip()
			for repetitive in [' ', '\n', '\t']:
				result = repetitive.join(result.split(repetitive))
		else:
			result = get_text(list(tags.children), sep=sep)
	else:
		result = []
		previous_tag = None
		for tag in tags:
			if tag is not None:
				text = get_text(tags=tag, sep=sep)
				if isinstance(text, str):
					text = text.strip()
				if text is not None and text != '':
					if isinstance(text, (tuple, list)) or len(result) == 0:
						result.append(text)
					elif not (hasattr(tag, 'children') and tag.children) and not (hasattr(previous_tag, 'children') and previous_tag.children):
						result[-1] += sep + text
					else:
						result.append(text)
				previous_tag = tag

	if flatten:
		result = flatten_list(result)
	return result
