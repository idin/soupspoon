from .is_break import is_break


def get_children(tag, ignore_single_children=True, extract=False):
	"""
	:type tag: Tag or list or tuple
	:rtype: NoneType or list[Tag]
	"""
	if isinstance(tag, (list, tuple)):
		return list(tag)

	if not hasattr(tag, 'children'):
		return None
	else:
		children = [x for x in tag.children if x is not None and x != []]
		if extract:
			children = [x.extract() for x in children]

		# remove repeated breaks
		new_children = []
		for child in children:
			if len(new_children) == 0:
				new_children.append(child)
			elif is_break(child) and is_break(new_children[-1]):  # ignore repeated break
				continue
			else:
				new_children.append(child)
		children = new_children

		if ignore_single_children:
			if len(children) == 1:
				return get_children(tag=children[0], ignore_single_children=ignore_single_children)

		if len(children) > 0:
			return children
		else:
			return None
