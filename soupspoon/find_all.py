from bs4 import BeautifulSoup, Tag, NavigableString


def element_is(element, name=None, attributes=None, text=None, ignore_name=None, ignore_attributes=None):
	if name is not None:
		if element.name != name:
			return False

	if attributes is not None:
		for key, value in attributes.items():
			if hasattr(element, 'attrs'):
				if key not in element.attrs:
					return False
				elif isinstance(element.attrs[key], list):
					if value not in element.attrs[key]:
						return False
				elif element.attrs[key] != value:
					return False
			else:
				return False

	if text is not None:
		if element.text != text:
			return False

	if ignore_name is None and ignore_attributes is None:
		return True
	elif ignore_attributes is None:
		return element.name != ignore_name
	elif ignore_name is None or element.name == ignore_name:
		for key, value in ignore_attributes.items():
			if hasattr(element, 'attrs'):
				if key not in element.attrs:
					return True
				elif isinstance(element.attrs[key], list):
					if value not in element.attrs[key]:
						return True
				elif element.attrs[key] != value:
					return True
			else:
				return True
		return False
	else:
		return True


def parent_is(element, name=None, attributes=None, text=None):
	if element.parent is None:
		return False
	else:
		return element_is(element.parent, name=name, attributes=attributes, text=text)


def child_is(element, name=None, attributes=None, text=None):
	if hasattr(element, 'children'):
		return any([element_is(element=child, name=name, attributes=attributes, text=text) for child in element.children])
	else:
		return False


def element_has(element, name=None, attributes=None, text=None):
	if element.find(name=name, attributes=attributes or {}):
		for t in element.find_all(name=name, attributes=attributes or {}):
			if text is None:
				return True
			elif t.text == text:
				return True
	return False


def find_all(elements, name=None, attributes=None, text=None, first_found=False, first_child=False, ignore_name=None, ignore_attributes=None):
	"""
	:param list[BeautifulSoup] or list[Tag] or list[str] or list[list] or Tag or BeautifulSoup elements:
	:param str or NoneType name:
	:param NoneType or dict attributes:
	:param NoneType or str text:
	:param bool first_found:
	:rtype: list[Tag] or list[BeautifulSoup]
	"""

	if isinstance(elements, (BeautifulSoup, Tag)):

		element = elements
		if element_is(
			element=element, name=name, attributes=attributes, text=text, ignore_name=ignore_name,
			ignore_attributes=ignore_attributes
		):
			return [element]

		else:

			if first_child:
				children = list(element.children)

				# remove empty navigable strings and ignored children
				children = [
					child for child in children
					if element_is(
						element=child, name=None, attributes=None,
						ignore_name=ignore_name, ignore_attributes=ignore_attributes
					)
				]
				# remove empty navigable strings and ignored children
				children = [x for x in children if not isinstance(x, NavigableString)]

				if len(children) > 0:
					if element_is(element=children[0], name=name, attributes=attributes, text=text):
						return [children[0]]
					elif element_has(element=children[0], name=name, attributes=attributes, text=text):
						return [find(elements=children[0], name=name, attributes=attributes, text=text)]
				else:
					return []

			elif first_found:

				for x in element.find_all(name=name, attrs=attributes or {}, text=text):
					if not element_is(element=x, name=ignore_name, attributes=ignore_attributes):
						return [x]

				return []

			else:

				results = element.find_all(name=name, attrs=attributes or {}, text=text)
				return [
					x for x in results
					if element_is(
						element=x, name=None, attributes=None,
						ignore_name=ignore_name, ignore_attributes=ignore_attributes
					)
				]
	elif isinstance(elements, str):

		return []

	else:

		result = [
			tag
			for element in elements or []
			for tag in find_all(
				elements=element, name=name, attributes=attributes, text=text,
				first_found=first_found, first_child=first_child,
				ignore_name=ignore_name, ignore_attributes=ignore_attributes
			) or []
		]
		return [tag for tag in result if tag is not None and tag != []]

	return []


def find(elements, name=None, attributes=None, text=None):
	"""
	:param list[BeautifulSoup] or list[Tag] or list[str] or list[list] or Tag or BeautifulSoup elements:
	:param str or NoneType name:
	:param NoneType or dict attributes:
	:param NoneType or str text:
	:param bool first_only:
	:rtype: Tag or BeautifulSoup or NoneType
	"""
	if isinstance(elements, (BeautifulSoup, Tag)):
		element = elements
		if element_is(element=element, attributes=attributes, text=text):
			return element
		else:
			return element.find(name=name, attrs=attributes or {}, text=text)
	elif isinstance(elements, str):
		return None
	else:
		for element in elements:
			tag = find(elements=element, name=name, attributes=attributes, text=text)
			if tag:
				return tag
		return None
