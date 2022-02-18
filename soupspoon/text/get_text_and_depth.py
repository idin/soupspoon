import re
from .get_style import get_style


def get_raw_text(tag):
	"""
	:type tag: Tag
	:rtype: NoneType or str
	"""
	if hasattr(tag, 'text'):
		text = tag.text
		if text is None:
			return None
	else:
		text = str(tag)

	return text


def is_break(tag):
	if tag.name == 'br':
		return True
	else:
		text = get_raw_text(tag)
		if text:
			if '\n' in text and text.strip() == '':
				return has_no_children(tag=tag)
			else:
				return False
		else:
			return False


def has_children(tag):
	return len(get_children(tag=tag)) > 0


def has_no_children(tag):
	return len(get_children(tag=tag)) == 0


def get_children(tag):
	"""
	:type tag: Tag or list or tuple
	:rtype: NoneType or list[Tag]
	"""
	if isinstance(tag, (list, tuple)):
		return list(tag)

	if not hasattr(tag, 'children'):
		return []

	else:
		children = [x for x in tag.children if x is not None and x != []]

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

		return children


def get_text_and_depth(tag, id, parent_id, depth, parent_style):
	"""
	:type tag: Tag
	:type id: str
	:type parent_id: str
	:type depth: int
	:type parent_style: dict
	:rtype: NoneType or str
	"""
	parent_style = parent_style or {}
	style = get_style(tag=tag)
	# merge styles with priority given to style
	style = {**parent_style, **style}

	children = get_children(tag)

	if len(children) == 0:
		text = get_raw_text(tag=tag)

		if text is not None:
			text = text.strip()

		if re.search(r'^\s*Page \d+$', text):
			text = None

		if text is None or len(text) == 0:
			return []
		else:
			return [{'id': id, 'parent_id': parent_id, 'depth': depth, 'text': text, **style}]

	else:
		result = []

		if len(id) > 0:
			id_prefix = f'{id}.'
		else:
			id_prefix = ''

		max_child_id_width = len(str(len(children)))

		for index, child in enumerate(children):
			child_partial_id = str(index + 1).rjust(max_child_id_width, '0')

			child_text_and_depth = get_text_and_depth(
				tag=child, id=f'{id_prefix}{child_partial_id}', parent_id=id,
				depth=depth + 1, parent_style=style
			)
			result += child_text_and_depth

		return result
