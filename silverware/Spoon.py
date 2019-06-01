from .find_all import find_all, element_is, element_has, parent_is, child_is, find
from .find_between import find_between, find_after, find_before, find_except
from .find_between import get_ancestors
from .find_between import get_siblings, get_preceding_siblings, get_succeeding_siblings
from .clone_beautiful_soup_tag import clone_beautiful_soup_tag
from .find_links import find_links
from .read_table import read_tables
from .get_lists import get_lists
from bs4 import BeautifulSoup, Tag
import warnings


class Spoon:
	def __init__(self, soup):
		"""
		:param list[Tag] or list[BeautifulSoup] or Tag or BeautifulSoup soup:
		"""
		if isinstance(soup, (Tag, BeautifulSoup)):
			self._soup = soup
		else:
			self._soup = list(soup)

	@property
	def soup(self):
		"""
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup]
		"""
		return self._soup

	def is_single(self):
		return isinstance(self._soup, (Tag, BeautifulSoup))

	@classmethod
	def clone(cls, soup, in_spoon=False):
		"""
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup] or Spoon
		"""
		if isinstance(soup, cls):
			soup = soup.soup
		result = clone_beautiful_soup_tag(elements=soup)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def copy(self):
		"""
		:rtype: Spoon
		"""
		return self.clone(soup=self.soup, in_spoon=True)

	def filter(self=None, name=None, attributes=None, text=None, first_only=False, in_spoon=True, soup=None):
		"""
		:param list[BeautifulSoup] or list[Tag] or list[str] or list[list] or Tag or BeautifulSoup or Spoon soup:
		:param str or NoneType name:
		:param NoneType or dict attributes:
		:param NoneType or str text:
		:param bool first_only:
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup] or Spoon
		"""
		if self is not None:
			soup = soup or self.soup
		if isinstance(soup, Spoon):
			soup = soup.soup

		result = find_all(elements=soup, name=name, attributes=attributes, text=text, first_only=first_only)
		if in_spoon:
			return Spoon(soup=result)
		else:
			return result

	def filter_out(self=None, in_spoon=True, soup=None):
		"""
		:param list[BeautifulSoup] or list[Tag] or list[str] or list[list] or Tag or BeautifulSoup or Spoon soup:
		:param str or NoneType name:
		:param NoneType or dict attributes:
		:param NoneType or str text:
		:param bool first_only:
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup] or Spoon
		"""
		if self is not None:
			soup = soup or self.soup
		if isinstance(soup, Spoon):
			soup = soup.soup

		result = find_except(element=soup)
		if in_spoon:
			return Spoon(soup=result)
		else:
			return result

	def find_all(self=None, name=None, attributes=None, text=None, in_spoon=True, soup=None):
		"""
		:param NoneType or BeautifulSoup or Tag soup:
		:param str or NoneType name:
		:param NoneType or dict attributes:
		:param NoneType or str text:
		:param bool first_only:
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup] or Spoon
		"""
		if self is not None:
			soup = soup or self.soup
		if isinstance(soup, Spoon):
			soup = soup.soup

		return self.filter(soup=soup, name=name, attributes=attributes, text=text, in_spoon=in_spoon)

	def find(self=None, name=None, attributes=None, text=None, in_spoon=True, soup=None):
		"""
		:param NoneType or BeautifulSoup or Tag soup:
		:param str or NoneType name:
		:param NoneType or dict attributes:
		:param NoneType or str text:
		:param bool first_only:
		:rtype: Tag or BeautifulSoup or NoneType or Spoon
		"""
		if self is not None:
			soup = soup or self.soup
		if isinstance(soup, Spoon):
			soup = soup.soup

		result = find(elements=soup, name=name, attributes=attributes, text=text)
		if in_spoon:
			return Spoon(soup=result)
		else:
			return result

	@classmethod
	def after(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = find_after(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_after(self, in_spoon=True):
		return self.after(element=self, in_spoon=in_spoon)

	@classmethod
	def before(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = find_before(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_before(self, in_spoon=True):
		return self.before(element=self, in_spoon=in_spoon)

	@classmethod
	def between(cls, element1, element2, in_spoon=True):
		if isinstance(element1, cls):
			element1 = element1.soup
		if isinstance(element2, cls):
			element2 = element2.soup
		result = find_between(element1=element1, element2=element2)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	@classmethod
	def parent(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = element.parent
		if result is None:
			warnings.warn('element does not have a parent!')
			result = element
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_parent(self, in_spoon=True):
		return self.parent(element=self.soup, in_spoon=in_spoon)

	@classmethod
	def children(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = element.children
		if result is None:
			raise RuntimeError('element does not have a children attribute!')
		elif len(result) == 0:
			warnings.warn('element does not have children!')
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	@classmethod
	def ancestors(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = get_ancestors(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_ancestors(self, in_spoon=True):
		return self.ancestors(element=self.soup, in_spoon=in_spoon)

	@classmethod
	def siblings(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = get_siblings(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_siblings(self, in_spoon=True):
		return self.siblings(element=self.soup, in_spoon=in_spoon)

	@classmethod
	def preceding_siblings(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = get_preceding_siblings(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_preceding_siblings(self, in_spoon=True):
		return self.preceding_siblings(element=self.soup, in_spoon=in_spoon)

	@classmethod
	def succeeding_siblings(cls, element, in_spoon=True):
		if isinstance(element, cls):
			element = element.soup
		result = get_succeeding_siblings(element=element)
		if in_spoon:
			return cls(soup=result)
		else:
			return result

	def get_succeeding_siblings(self, in_spoon=True):
		return self.succeeding_siblings(element=self.soup, in_spoon=in_spoon)

	@property
	def text(self):
		return self.soup.text

	@property
	def attributes(self):
		return self.soup.attrs

	def __getitem__(self, item):
		return self.soup[item]

	def element_is(self=None, element=None, name=None, attributes=None, text=None):
		if self is not None:
			element = element or self.soup
		return element_is(element=element, name=name, attributes=attributes, text=text)

	def parent_is(self=None, element=None, name=None, attributes=None, text=None):
		if self is not None:
			element = element or self.soup
		return parent_is(element=element, name=name, attributes=attributes, text=text)

	def child_is(self=None, element=None, name=None, attributes=None, text=None):
		if self is not None:
			element = element or self.soup
		return child_is(element=element, name=name, attributes=attributes, text=text)

	@classmethod
	def element_has(cls, element, name=None, attributes=None, text=None):
		if isinstance(element, cls):
			element = element.soup
		return element_has(element=element, name=name, attributes=attributes, text=text)

	def has(self, name=None, attributes=None, text=None):
		return self.element_has(element=self.soup, name=name, attributes=attributes, text=text)

	def find_links(self=None, element=None, base_url=None):
		if self is not None:
			element = element or self.soup
		return find_links(elements=element, base=base_url)

	def read_tables(self=None, element=None, attributes=None, text=None, parse_links=False, base_url=None):
		if self is not None:
			element = element or self.soup
		return read_tables(
			tables=find_all(elements=element, name='table', attributes=attributes or {}, text=text),
			parse_links=parse_links, base_url=base_url
		)

	def read_table(self=None, element=None, attributes=None, text=None, parse_links=False, base_url=None):
		result = Spoon.read_tables(self=self, element=element, attributes=attributes, text=text, parse_links=parse_links, base_url=base_url)
		if len(result) > 0:
			return result[0]
		else:
			return None

	def get_lists(self=None, element=None, links_only=False, base_url=None):
		if self is not None:
			element = element or self.soup
		return get_lists(elements=element, links_only=links_only, base=base_url)
