from bs4 import BeautifulSoup, Tag


def get_same_type_siblings(element):
	"""
	:type element: BeautifulSoup or Tag
	:rtype: list[Tag]
	"""
	parent = element.parent
	siblings = [x for x in parent.find_all(name=element.name) if x.parent == element.parent]
	precedings = []
	followings = []

	pointer = precedings
	for s in siblings:
		if s == element:
			pointer = followings
		else:
			pointer.append(s)
	return {'preceding': precedings, 'following': followings}


def get_next_same_type_sibling(element):
	"""
		:type element: BeautifulSoup or Tag
		:rtype: list[Tag]
		"""
	parent = element.parent
	found_self = False
	for x in parent.find_all(name=element.name):
		if x.parent == element.parent:
			if x == element:
				found_self = True
			elif found_self:
				return x
	return None
