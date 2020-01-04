from bs4 import Tag, NavigableString, BeautifulSoup
from .exceptions import ElementTypeError

def clone_beautiful_soup_tag(elements):
	"""
	:type element: Tag
	:rtype: Tag
	"""
	if elements is None:
		raise ElementTypeError('elements is None!')

	if isinstance(elements, (Tag, NavigableString, BeautifulSoup)):
		element = elements
		if isinstance(element, NavigableString):
			return type(element)(element)

		copy = Tag(None, element.builder, element.name, element.namespace, element.nsprefix)

		# work around bug where there is no builder set
		# https://bugs.launchpad.net/beautifulsoup/+bug/1307471
		copy.attrs = dict(element.attrs)
		for attr in ('can_be_empty_element', 'hidden'):
			setattr(copy, attr, getattr(element, attr))
		for child in element.contents:
			copy.append(clone_beautiful_soup_tag(child))
		return copy
	else:
		return [clone_beautiful_soup_tag(x) for x in elements]

