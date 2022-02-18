from bs4 import BeautifulSoup, Tag


def soup_has_element(soup, element):
	result = soup.find_all(name=element.name, attrs=element.attrs)
	if element.text is None:
		return len(result) > 0
	else:
		for x in result:
			if x.text == element.text:
				return True
		return False


def get_ancestors(element):
	yield element
	while element.parent:
		element = element.parent
		yield element


def get_mutual_ancestor(element1, element2):
	ancestors1 = {id(ancestor): ancestor for ancestor in get_ancestors(element1)}
	for ancestor in get_ancestors(element2):
		if id(ancestor) in ancestors1:
			return ancestor


def get_mutual_and_non_mutual_ancestors(element1, element2):
	ancestors1 = {id(ancestor): ancestor for ancestor in get_ancestors(element1)}
	ancestors2 = {id(ancestor): ancestor for ancestor in get_ancestors(element2)}
	mutual = None

	non_mutuals1 = []
	for key, ancestor in ancestors1.items():
		if key in ancestors2:
			break
		else:
			non_mutuals1.append(ancestor)

	non_mutuals2 = []
	for key, ancestor in ancestors2.items():
		if key in ancestors1:
			mutual = ancestor
			break
		else:
			non_mutuals2.append(ancestor)

	return mutual, non_mutuals1, non_mutuals2

def get_siblings_and_self(element):
	if element.parent is not None:
		return element.parent.children
	else:
		return []

def get_siblings(element):
	return [x for x in get_siblings_and_self(element) if x != element]

def get_succeeding_siblings(element):
	siblings = get_siblings_and_self(element)
	result = []
	self_is_seen = False
	for x in siblings:
		if self_is_seen:
			result.append(x)
		elif id(x) == id(element):
			self_is_seen = True
	return result


def get_preceding_siblings(element):
	siblings = get_siblings_and_self(element)
	result = []
	for x in siblings:
		if id(x) == id(element):
			break
		else:
			result.append(x)
	return result


def find_between(element1, element2):
	mutual, ancestors1, ancestors2 = get_mutual_and_non_mutual_ancestors(element1=element1, element2=element2)
	ancestors1_ids = [id(x) for x in ancestors1]
	ancestors2_ids = [id(x) for x in ancestors2]

	left_side = [uncle for ancestor in ancestors1[:-1] for uncle in get_succeeding_siblings(ancestor)]
	right_side = [aunt for ancestor in ancestors2[:-1][::-1] for aunt in get_preceding_siblings(ancestor)]

	middle = []
	start_children = False
	if mutual is not None:
		if mutual.children is not None:
			for child in mutual.children:
				if start_children:
					if id(child) in ancestors2_ids:
						break
					else:
						middle.append(child)
				elif id(child) in ancestors1_ids:
					start_children = True

	return left_side + middle + right_side


def find_after(element):
	if not isinstance(element, (BeautifulSoup, Tag)):
		raise TypeError(f'{type(element)} is not accepted!')
	ancestors = list(get_ancestors(element))
	return [uncle for ancestor in ancestors[:-1] for uncle in get_succeeding_siblings(ancestor)]


def find_before(element):
	if not isinstance(element, (BeautifulSoup, Tag)):
		raise TypeError(f'{type(element)} is not accepted!')
	ancestors = list(get_ancestors(element))
	return [aunt for ancestor in ancestors[:-1][::-1] for aunt in get_preceding_siblings(ancestor)]


def find_except(element):
	if not isinstance(element, (BeautifulSoup, Tag)):
		raise TypeError(f'{type(element)} is not accepted!')
	return find_before(element=element) + find_after(element=element)
