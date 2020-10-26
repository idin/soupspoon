from txt import wrap
MAX_WIDTH = 88


class Section:
	def __init__(self, title, body=None, parent=None, font_size=None, children_font_size=None):
		"""
		:type title: str
		:type body: list[str] or str
		:type parent: Section
		"""
		self._title = title
		if isinstance(body, str):
			body = [body]

		self._body = body or []
		self._parent = None
		self._subsections = []
		self._font_size = None
		self._children_font_size = children_font_size

		self.parent = parent

	def display_title(self):
		return f'{"*" * (self.depth + 1)} {self._title} {"*" * (self.depth + 1)}'

	def __str__(self):
		title_wrap = wrap(text=self.display_title(), indentation="  " * self.depth, max_width=MAX_WIDTH)
		text_wraps = [wrap(text=text, indentation="  " * self.depth, max_width=MAX_WIDTH) for text in self.body]
		return '\n\n'.join([title_wrap] + text_wraps)

	def __repr__(self):
		return str(self)

	def __gt__(self, other):
		"""
		:type other: Section
		:rtype: bool
		"""
		if self._font_size is not None and other._font_size is not None:
			return self._font_size > other._font_size

		elif self._children_font_size is not None and other._font_size is not None:
			return self._children_font_size >= other._font_size

		else:
			return False

	@property
	def depth(self):
		if self.parent is None:
			return 0
		else:
			return self.parent.depth + 1

	@property
	def body(self):
		"""
		:rtype: list[str]
		"""
		return self._body

	def append_text(self, text):
		if self._body is None:
			self._body = []

		if isinstance(text, str):
			self._body.append(' '.join(text.split(sep=' ')))
		elif isinstance(text, list):
			for x in text:
				self.append_text(text=x)

	@property
	def subsections(self):
		"""
		:rtype: list[Section]
		"""
		return self._subsections

	@property
	def parent(self):
		"""
		:rtype: NoneType or Section
		"""
		return self._parent

	@parent.setter
	def parent(self, parent):
		"""
		:type parent: NoneType or Section
		"""
		if self._parent is not None:
			raise RuntimeError('section has a parent already!')

		self._parent = parent
		if parent is not None:
			parent.subsections.append(self)
