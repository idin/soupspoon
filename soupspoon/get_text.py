from bs4 import BeautifulSoup, Tag, NavigableString
from slytherin.collections import flatten as flatten_list


def is_text(tag):
	if isinstance(tag, (str, NavigableString)):
		return True
	try:
		if tag.name == 'br' or tag.name == 'span':
			return True
	except:
		pass
	return False


def is_title(tag):
	try:
		if tag.name == 'span' and list(tag.children)[-1].name == 'br':
			return True
	except:
		pass
	return False

def get_children(tag):
	if not hasattr(tag, 'children'):
		return None
	else:
		children = [x for x in tag.children if x is not None and x != []]
		if len(children) > 0:
			return children
		else:
			return None


def has_children(tag):
	return get_children(tag) is not None


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
				if text is not None:
					if isinstance(text, (tuple, list)) or len(result) == 0 or is_title(tag):
						result.append(text)
					elif not has_children(tag) and not has_children(previous_tag):
						result[-1] += sep + text
					else:
						result.append(text)
				previous_tag = tag
		result = [x for x in result if x is not None and x != '']

	if flatten:
		result = flatten_list(result)
	return result
