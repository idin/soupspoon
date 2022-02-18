from .clean_html_text import clean_html_text
from bs4 import BeautifulSoup
from bs4.element import Tag

class Link:
	def __init__(self, element=None, url=None, text=False, base=None):
		"""

		:type element: BeautifulSoup or Tag or NoneType
		:type url: str or NoneType
		:type text: str or NoneType
		:type base: str or NoneType
		"""
		if element is not None:
			a = element.find('a')
			if a:
				element = a

		if url is None:
			if element is None:
				raise ValueError('either url or element should be provided!')
			self._url = self.get_url(element=element, base=base)
		else:
			self._url = url
		self._text = text or self.get_text(element=element) or self._url

	def __getstate__(self):
		return self._url, self._text

	def __setstate__(self, state):
		self._url, self._text = state

	def __hashkey__(self):
		"""
		used in smart_hash function
		:type: str
		"""
		return (repr(self.url), repr(self.__class__))

	def __hash__(self):
		return hash((self.url, repr(self.__class__)))

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.url == other.url
		else:
			return self.url == other

	def __str__(self):
		return f'{self.text} {self.url} '

	def __repr__(self):
		return str(self)

	def is_anchor(self):
		"""
		:rtype: bool
		"""
		return self._url.startswith('#')

	@property
	def text(self):
		"""
		:rtype: str
		"""
		return self._text

	@property
	def url(self):
		"""
		:rtype: str
		"""
		return self._url

	@staticmethod
	def get_url(element, base=None):
		"""
		:type element: BeautifulSoup or Tag
		:type base: str
		:rtype: str
		"""
		try:
			href = element['href']
		except KeyError:
			raise AttributeError('element does not have a url!')

		if href.startswith('http://') or href.startswith('https://') or base is None or href.startswith('#'):
			return href
		elif href.startswith('/'):
			if base is None:
				raise TypeError('no base is provided!')
			else:
				return base + href

	@staticmethod
	def get_text(element):
		"""
		:type element: BeautifulSoup or Tag
		:rtype: str
		"""
		if element is None:
			return None
		try:
			return clean_html_text(html=element, replace_images=True)
		except AttributeError:
			return None

def parse_link(element, base=None, ignore_anchor=False):
	"""
	parses an element and returns the link or None or
	:type element: BeautifulSoup or Tag
	:type base: str or NoneType
	:type ignore_anchor: bool
	:rtype: Link or str or NoneType
	"""
	if element is None:
		return None
	try:
		link = Link(element=element, base=base)
		if link.is_anchor():
			if ignore_anchor:
				return None
			else:
				return clean_html_text(html=element, replace_images=True)
		else:
			return link
	except AttributeError:
		return clean_html_text(html=element, replace_images=True)

def find_links(elements, base=None, ignore_anchors=False):
	"""
	parses multiple elements and returns links as a list of Links
	:type element: BeautifulSoup or Tag
	:type base: str or NoneType
	:type ignore_anchor: bool
	:rtype: list[Link]
	"""
	if isinstance(elements, (BeautifulSoup, Tag)):
		if elements.name == 'a':
			links = [elements]
		else:
			links = elements.find_all(name='a')

		if links is None:
			return []
		else:
			result = [parse_link(element=link, base=base, ignore_anchor=ignore_anchors) for link in links if link is not None]
			return [x for x in result if isinstance(x, Link)]

	elif isinstance(elements, str) or elements is None:
		return []
	else:
		return [link for element in elements for link in find_links(elements=element, base=base)]
