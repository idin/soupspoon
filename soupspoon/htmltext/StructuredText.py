from .Section import Section
from .Section import MAX_WIDTH
from .is_body_text import is_body_text
from .is_bullet_point import is_bullet_heading
from .is_bullet_point import has_bullet


class StructuredText:
	def __init__(self, html_text):
		"""
		:type html_text: BaseHtmlText
		"""
		self._sections_dictionary = {}
		self._sections = []
		self._record_parents = {}

		self._title_font_size_min = html_text.font_sizes['title_min']
		self._body_font_size = html_text.font_sizes['body']
		self._section_stack = []
		self._bullet_heading = None
		self._bullet_point = None
		for record in html_text.records:
			self.add_record(record=record)

	def __getitem__(self, item):
		return self._sections_dictionary[item]

	def __setitem__(self, key, value):
		if key in self._sections_dictionary:
			raise KeyError(f'{key} already exists!')
		self._sections_dictionary[key] = value
		self.sections.append(value)
		self.section_stack.append(value)

	def __contains__(self, item):
		return item in self._sections_dictionary

	@property
	def sections(self):
		"""
		:rtype: list[Section]
		"""
		return self._sections

	@property
	def section_stack(self):
		"""
		:rtype: list[Section]
		"""
		return self._section_stack

	@property
	def last_section(self):
		"""
		:rtype: Section or NoneType
		"""
		if len(self.section_stack) < 1:
			return None
		else:
			return self.section_stack[-1]

	def reset_bullet(self):
		self._bullet_heading = None
		self._bullet_point = None

	def create_section_with_no_title_if_there_is_no_section(self, font_size):
		if self.last_section is None:
			new_section = Section(title='No Title', children_font_size=font_size)
			self[-1] = new_section

	def add_record(self, record):
		key = record['id']
		text = record['text']
		font_size = record['font_size']
		children_font_size_max = record['children_font_size_max']

		if text is not None:
			text = text.strip()
			if 'I use an exchange rate of ' in text:
				raise

		if font_size is not None and text is not None and len(text) > 1:

			# capture text and add them to the last section
			# if last section doesn't exist create a new section and add the text to it
			if font_size == self._body_font_size and is_body_text(text=text):

				self.create_section_with_no_title_if_there_is_no_section(font_size=font_size)
				self.last_section.append_text(text=text)
				self.reset_bullet()

			# capture section
			# if it is smaller than the last section, make the last section its parent
			# otherwise pop out the last section from the stack until you find a proper parent
			elif font_size >= self._title_font_size_min:

				section = Section(title=text, font_size=font_size, children_font_size=children_font_size_max)
				while self.last_section is not None:
					if self.last_section > section:
						section.parent = self.last_section
						break
					else:
						self.section_stack.pop()
				self[key] = section
				self.reset_bullet()

			elif font_size < self._title_font_size_min or font_size == self._body_font_size:
				# check for bullet points

				if self._bullet_heading is None:

					if is_bullet_heading(text):
						self.reset_bullet()
						self._bullet_heading = text

				elif self._bullet_heading is not None and has_bullet(text):

					self.create_section_with_no_title_if_there_is_no_section(font_size=font_size)

					if self._bullet_heading is not True:
						self.last_section.append_text(text=self._bullet_heading)
						self._bullet_heading = True # no text, just a confirmation that it is added

					self.last_section.append_text(text=text)
					self._bullet_point = True

				elif has_bullet(text):

					if self._bullet_point is None:
						self._bullet_point = text

					elif self._bullet_point is True:
						# previous was a bullet point and is already added
						self.create_section_with_no_title_if_there_is_no_section(font_size=font_size)
						self.last_section.append_text(text)

					elif isinstance(self._bullet_point, str):
						# previous was a bullet point but i had to verify with this one first
						# so it wasn't added
						self.create_section_with_no_title_if_there_is_no_section(font_size=font_size)
						self.last_section.append_text(self._bullet_point)
						self.last_section.append_text(text)
						self._bullet_point = True

	def __str__(self):
		return f'\n\n{"─"*MAX_WIDTH}\n\n'.join([str(s) for s in self._sections])

	def __repr__(self):
		return str(self)
