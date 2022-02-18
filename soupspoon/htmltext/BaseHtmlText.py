from bs4 import Tag
from txt import wrap
from pandas import DataFrame
from joblib import Parallel
from joblib import delayed
from slytherin.numbers import divide_into_almost_equal_parts

from .get_font_size import get_font_size
from .get_font_size import get_style
from .get_children import get_children
from .get_text import get_text


class BaseHtmlText:
	def __init__(self, obj, _id, extract_tags, ignore_function=None, depth=0, ids=None, log=None, num_jobs=1):
		"""
		:type obj: 				Tag or BaseHtmlText or Pdf
		:type ignore_function: 	Callable or NoneType
		"""
		if isinstance(obj, BaseHtmlText):
			ignore_function = ignore_function or obj._ignore_function
			depth = max(depth, obj._production_depth)
			obj = obj._tag
			if extract_tags:
				obj._tag = None
		else:
			try:
				if extract_tags:
					obj = obj.html_file.extract_soup()
				else:
					obj = obj.html_file.soup
			except AttributeError:
				pass

		self._tag = obj
		self._parent = None
		self._children = []
		self._string = None
		self._num_strings = 0
		self._font_size = get_font_size(tag=obj)
		self._style = get_style(tag=obj)
		self._complete_style = None
		self._production_depth = depth
		self._ignore_function = ignore_function
		self._index = None
		self._ids = ids or {}
		self._num_jobs = num_jobs

		if log is None or log is False or log == 0:
			self._logs = None
		elif isinstance(log, list):
			self._logs = log
		else:
			self._logs = []

		self._id = str(_id)
		self._ids[self.id] = self
		self.parse(tag=obj, extract_tags=extract_tags)

	@classmethod
	def _get_state_attribute_names(cls):
		return {
			'_children': [],
			'_string': None,
			'_num_strings': 0,
			'_font_size': None,
			'_style': None,
			'_complete_style': None,
			'_production_depth': 0,
			'_index': None,
			'_id': 1,
			'_num_jobs': 1
		}

	@classmethod
	def _get_empty_attribute_names(cls):
		return {
			'_tag': None,
			'_parent': None,
			'_ignore_function': None,
			'_logs': [],
			'_ids': {}
		}

	def __repr__(self):
		return f'<HtmlText: {str(self)}>'

	def __str__(self):
		result = self.string
		for child in self.children:
			result += ' ' + str(child)

		if len(result) > 64:
			return f'{result[:60]} ...'
		else:
			return result

	def __getstate__(self):
		return {key: getattr(self, key) for key in self._get_state_attribute_names().keys()}

	def __setstate__(self, state):
		dictionary = {**self._get_empty_attribute_names(), **self._get_empty_attribute_names(), **state}

		for key, value in dictionary.items():
			try:
				setattr(self, key, value)
			except AttributeError:
				print(f"can't set attribute \"{key}\" to \"{value}\"")
				raise AttributeError(f"can't set attribute \"{key}\" to \"{value}\"")

		for child in self.children:
			child._parent = self

	def _set_logs(self, logs):
		self._logs = logs
		for child in self.children:
			child._set_logs(logs=logs)

	def _set_ids(self, ids):
		self._ids = ids
		for child in self.children:
			child._set_ids(ids=ids)

	def delete(self, by):
		if self.id is not None:
			self.log('delete', by=by)
			self._ids[self.id] = None
		if self.parent:
			try:
				self.parent.children.remove(self)
			except ValueError:
				pass

	@property
	def id(self):
		"""
		:rtype: int or NoneType
		"""
		return self._id

	@property
	def logs(self):
		"""
		:rtype: DataFrame or NoneType
		"""
		if self._logs is None:
			return None
		else:
			return DataFrame.from_records(self._logs)

	def log(self, message, by):
		if self._logs is not None and self.id is not None:
			self._logs.append({'id': self.id, 'message': message, 'by': by.id})

	@property
	def depth(self):
		"""
		:rtype: int
		"""
		if self.parent is not None:
			return self.parent.depth + 1
		else:
			return 0

	@property
	def string(self):
		"""
		:rtype: str
		"""
		if self._string is None:
			return ''
		else:
			return self._string.strip()

	@string.setter
	def string(self, string):
		"""
		:type string: str
		"""
		if not isinstance(string, str):
			raise TypeError(f'{string} is of type {type(string)}')
		if self._string is not None:
			raise ValueError(f'cannot overwrite string "{self._string}" with "{string}"')
		self.log(message=f'add string "{string}"', by=self)
		self._string = string
		self._num_strings = 1

	@property
	def string_for_display(self):
		"""
		:rtype: str
		"""
		if self.string == '':
			return ''
		else:
			string = self.string
			if len(string) > 0 and self.font_size is not None:
				return f'{self.index_string} {string} ({self.font_size})'
			else:
				return string

	def ignore_string(self, string):
		if self._ignore_function is None:
			return False
		else:
			return self._ignore_function(string)

	@property
	def tag(self):
		"""
		:rtype: Tag
		"""
		return self._tag

	@property
	def font_size(self):
		"""
		:rtype: int or float or NoneType
		"""
		if self.parent is None:
			return self._font_size
		else:
			return self._font_size or self.parent.font_size

	@property
	def style(self):
		"""
		:rtype: dict[str, str]
		"""
		if self._complete_style is None:
			if self.parent is None or self.parent.style is None:
				self._complete_style = self._style
			elif self._style is None:
				self._complete_style = self.parent.style
			else:
				self._complete_style = {**self.parent.style, **self._style}
		return self._complete_style

	@property
	def children_font_size_max(self):
		if self.num_children == 0:
			return None
		else:
			font_sizes = [
				child.font_size if child.font_size is not None else child.children_font_size_max
				for child in self.children
			]
			font_sizes = [x for x in font_sizes if x is not None]
			if len(font_sizes) > 0:
				return max(font_sizes)
			else:
				return None

	@property
	def children(self):
		"""
		:rtype: list[BaseHtmlText] or None
		"""
		return self._children

	@property
	def parent(self):
		"""
		:rtype: BaseHtmlText or NoneType
		"""
		return self._parent

	@parent.setter
	def parent(self, parent):
		"""
		:type parent: BaseHtmlText
		"""
		if not isinstance(parent, BaseHtmlText):
			raise TypeError(f'parent {parent.id} is of type {type(parent)}')
		parent.log(f'become parent of {self.id}', by=self)
		self._parent = parent
		self._index = parent.num_children
		parent.children.append(self)

	@property
	def index(self):
		if self.parent is None:
			return 0
		elif self._index is None:
			return -1
		else:
			return self._index

	@property
	def index_string(self):
		if self.parent is not None:
			max_width = len(str(self.parent.num_children - 1))
			return str(self.index).rjust(max_width, '0')
		else:
			return ''

	@property
	def num_children(self):
		if self._children is None:
			return 0
		else:
			return len(self._children)

	@property
	def num_siblings(self):
		if self.parent is None:
			return 0
		else:
			return self.parent.num_children - 1

	@property
	def rank_among_siblings(self):
		if self.parent is None:
			return 1
		else:
			try:
				return self.parent.children.index(self) + 1
			except ValueError:
				return -1

	@property
	def last_child(self):
		"""
		:rtype: BaseHtmlText or NoneType
		"""
		if self.num_children == 0:
			return None
		else:
			return self.children[-1]

	def is_just_text(self):
		return self._string is not None and self.num_children == 0

	def is_only_parent(self):
		return self._string is None and self.num_children > 0

	def parse(self, tag, extract_tags):
		tag_children = get_children(tag, ignore_single_children=False, extract=extract_tags)
		if tag_children is None:
			tag_children = []
		if len(tag_children) == 0:
			self.string = (get_text(tag) or '').lstrip('-*\t .')

		else:
			self.parse_children(tag_children=tag_children, extract_tags=extract_tags)

	def absorb_children(self, other, by):
		"""
		:type other: BaseHtmlText
		:type by: BaseHtmlText
		"""
		self.log(message=f'absorb children of {other}', by=by)
		for child in other.children:
			child.parent = self
		other._children = []
		other.delete(by=by)

	def join_text_children(self):
		self.log(message='join text children', by=self)
		children = self.children
		self._children = []

		for child in children:
			prev_child = self.last_child
			if prev_child is None:
				child.parent = self

			# absorb
			elif prev_child.font_size == child.font_size or prev_child.font_size is None or child.font_size is None:
				prev_child._string += '\n' + child._string
				prev_child._num_strings = prev_child._num_strings + child._num_strings
				child._num_strings = 0
				child.delete(by=self)
				prev_child._font_size = prev_child._font_size or child._font_size

	def absorb_font_and_style(self, html_text):
		"""
		:type html_text: BaseHtmlText
		"""
		self._font_size = html_text._font_size or self._font_size
		if self._style is None:
			self._style = html_text._style
		elif html_text._style is None:
			pass
		else:
			self._style = {**html_text._style, **self._style}

	def absorb_grand_children(self):
		if len(self.children) != 1:
			raise RuntimeError('cannot absorb grand children when there are more than one child')

		single_child = self.children[0]

		if single_child.is_just_text() and self.string == '':
			self.log(message=f'absorb text from child {single_child.id}', by=self)
			self._children = []
			self.string = single_child._string
			self._num_strings = single_child._num_strings
			single_child._string = None
			single_child._num_strings = 0
			self.absorb_font_and_style(html_text=single_child)
			single_child.delete(by=self)

		elif single_child.is_only_parent():
			self.log(message=f'absorb grand children from child {single_child.id}', by=self)
			self._children = []
			for grand_child in single_child.children:
				grand_child.parent = self
			self.absorb_font_and_style(html_text=single_child)
			single_child.delete(by=self)

		# if single child is both parent and string
		elif self.string == '':
			self.log(message=f'absorb text from child {single_child.id}', by=self)
			self.string = single_child.string
			self._num_strings = single_child._num_strings
			single_child._string = None
			single_child._num_strings = 0
			for grand_child in single_child.children:
				grand_child.parent = self
			self.absorb_font_and_style(html_text=single_child)
			single_child.delete(by=self)
		else:
			self.log(message=f'cannot absorb anything from child {single_child.id}', by=self)

	def _get_tag_and_child(self, tag, num_jobs, child_id, extract_tags):
		base_html_text = BaseHtmlText(
			obj=tag,
			_id=f'{self.id}.{child_id}',
			depth=self._production_depth + 1,
			log=self._logs,
			ids=self._ids,
			extract_tags=extract_tags,
			num_jobs=num_jobs
		)
		return tag, base_html_text

	def get_tags_and_children(self, tag_children, extract_tags):
		num_jobs_remaining = self._num_jobs - 1
		num_jobs_per_child = divide_into_almost_equal_parts(number=num_jobs_remaining, by=len(tag_children))
		child_ids = [i + 1 for i in range(len(tag_children))]

		if self._num_jobs < 2:
			tags_and_children = [
				self._get_tag_and_child(tag=_tag, num_jobs=1, child_id=_child_id, extract_tags=extract_tags)
				for _tag, _child_id in zip(tag_children, child_ids)
			]

		elif any([x < 1 for x in num_jobs_per_child]):
			tags_and_children = [
				self._get_tag_and_child(tag=_tag, num_jobs=1, child_id=_child_id, extract_tags=extract_tags)
				for _tag, _child_id in zip(tag_children, child_ids)
			]

		else:
			tags_and_num_jobs_and_ids = list(zip(tag_children, num_jobs_per_child, child_ids))

			processor = Parallel(n_jobs=self._num_jobs, backend='threading', require='sharedmem')
			tags_and_children = processor(
				delayed(self._get_tag_and_child)(
					tag=_tag,
					num_jobs=int(_num_jobs),
					child_id=_child_id,
					extract_tags=extract_tags
				)
				for _tag, _num_jobs, _child_id in tags_and_num_jobs_and_ids
			)

		return tags_and_children

	def parse_children(self, tag_children, extract_tags):

		tags_and_children = self.get_tags_and_children(tag_children=tag_children, extract_tags=extract_tags)

		for tag, child in tags_and_children:
			prev_child = self.last_child

			if child.num_children == 0 and child.string == '':
				# ignore useless children
				child.log("no children and no string", by=self)
				child.delete(by=self)
				continue

			elif child.num_children == 0 and self.ignore_string(string=child.string):
				child.log("no children and ignore string", by=self)
				child.delete(by=self)
				continue

			else:

				if prev_child is None:
					child.parent = self

				else:
					if prev_child.font_size == child.font_size or prev_child.font_size is None or child.font_size is None:
						# absorb if the two children are parents in the same level
						if prev_child.is_only_parent() and child.is_only_parent():
							prev_child.absorb_children(other=child, by=self)

						else:
							child.parent = self

					elif prev_child.font_size > child.font_size:
						child.parent = prev_child

					elif prev_child.font_size < child.font_size:
						child.parent = self

		# if all children are just text join them together
		if all([child.is_just_text() for child in self.children]):
			self.join_text_children()

		# absorb children of the one child
		if self.num_children == 1:
			self.absorb_grand_children()

	def display_string(self, max_width, depth_decrease=0):

		if len(self.string) > 0:
			indentation = '  ' * (self.depth - depth_decrease)
			return wrap(
				text=f'< {self.string_for_display} >',
				max_width=max_width,
				indentation=indentation,
				prefix='|',
				suffix='|'
			)

		else:
			result = ''

		return result

	def display(self, max_width=90, depth_decrease=None):
		"""
		displays the HtmlText and all its children
		:rtype: str
		"""
		if depth_decrease is None:
			depth_decrease = self.depth

		result = self.display_string(max_width=max_width, depth_decrease=depth_decrease)

		for child in self.children:
			child_string = child.display(max_width=max_width, depth_decrease=depth_decrease)
			if len(child_string) > 0 and len(result) > 0:
				result += '\n' + child_string
			else:
				result += child_string

		return result

	def print(self, max_width=90):
		return print(self.display(max_width=max_width))

	def __getitem__(self, item):
		if isinstance(item, int):
			return self.children[item]
		elif isinstance(item, str):
			for child in self.children:
				if child._string.strip().lower().startswith(item.lower()):
					return child
			raise KeyError(f'{item} does not exist!')

	@property
	def record(self):
		"""
		:rtype: dict[str, ]
		"""
		return {
			'id': self.id,
			'parent_id': self.parent.id if self.parent is not None else 0,
			'depth': self.depth,
			'index': self.index,
			'font_size': self.font_size,
			'children_font_size_max': self.children_font_size_max,
			'rank_among_siblings': self.rank_among_siblings,
			'num_siblings': self.num_siblings,
			'num_children': self.num_children,
			'num_characters': len(self.string),
			'num_strings': self._num_strings,
			'text': self.string,
			**self.style
		}

	@property
	def records(self):
		"""

		:rtype: list[dict[str, ]]
		"""
		result = [self.record]
		for child in self.children:
			result += child.records
		return result

	@property
	def simple_records(self):
		if self.string != '':
			result = [{'font_size': self.font_size, 'text': self.string}]
		else:
			result = []

		for child in self.children:
			result += child.simple_records

		return result
