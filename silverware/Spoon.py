from .find_all import find_all, element_is, element_has, parent_is, child_is, find
from .find_between import find_between, find_after, find_before, find_except
from .find_between import get_ancestors
from .find_between import get_siblings, get_preceding_siblings, get_succeeding_siblings
from .clone_beautiful_soup_tag import clone_beautiful_soup_tag
from .find_links import find_links, parse_link
from .read_table import read_tables
from .get_lists import get_lists
from .get_same_type_siblings import get_next_same_type_sibling
from .clean_name import clean_name
from .flatten_dictionaries_and_lists import flatten_dictionaries_and_lists
from .get_text import get_text

from bs4 import BeautifulSoup, Tag, NavigableString, PageElement
import warnings


class Spoon:
	def __init__(self, soup):
		"""
		:param list[Tag] or list[BeautifulSoup] or Tag or BeautifulSoup soup or Spoon or list[Spoon]:
		"""
		if isinstance(soup, (Tag, BeautifulSoup, NavigableString)):
			self._soup = soup
		elif isinstance(soup, Spoon):
			self._soup = soup.soup
		else:
			self._soup = []
			for x in soup:
				if isinstance(x, (Tag, BeautifulSoup, NavigableString)):
					self._soup.append(x)
				elif isinstance(x, Spoon):
					self._soup.append(x.soup)
				else:
					raise TypeError(f'soup cannot consist of "{x}" whose type is {type(x)}')

	def extract(self):
		if isinstance(self._soup, Spoon):
			return self._soup.extract()
		elif isinstance(self._soup, (Tag, BeautifulSoup, NavigableString)):
			return self._soup.extract()
		else:
			return [x.extract() for x in self._soup]

	def __repr__(self):
		return str(self)

	def __str__(self):
		if isinstance(self._soup, list):
			return '\n'.join([str(x) for x in self._soup])
		else:
			return str(self._soup)

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

	def filter(
			self=None, name=None, attributes=None, text=None, first_only=False, in_spoon=True, soup=None,
			first_child=False, ignore_name=None, ignore_attributes=None
	):
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

		result = find_all(
			elements=soup, name=name, attributes=attributes, text=text,
			first_found=first_only, first_child=first_child,
			ignore_name=ignore_name, ignore_attributes=ignore_attributes
		)
		if in_spoon:
			return Spoon(soup=result)
		else:
			return result

	def get_sections(self=None, sections=None, soup=None, in_spoon=True):
		"""
		:type sections: str or list
		:type soup: list[BeautifulSoup] or list[Tag] or list[str] or list[list] or Tag or BeautifulSoup or Spoon
		:type in_spoon: bool
		:rtype: Tag or BeautifulSoup or list[Tag] or list[BeautifulSoup] or Spoon
		"""
		if self is not None:
			soup = soup or self.soup
		if isinstance(soup, Spoon):
			soup = soup.soup

		if isinstance(sections, str):
			sections = [sections]

		headings = find_all(elements=soup, name=[f'h{i}' for i in range(10)])
		spoons = []
		for section_name in sections:
			for header in headings:
				if header.text.lower().startswith(section_name.lower()):
					next_header = get_next_same_type_sibling(header)
					if next_header is None:
						spoon = Spoon(soup=soup).after(element=header)
					else:
						spoon = Spoon(soup=soup).between(element1=header, element2=next_header)
					spoons.append(spoon)
					break
			else:
				raise KeyError(f'section "{section_name}" not found!')

		result = Spoon(soup=spoons)
		if in_spoon:
			return result
		else:
			return result.soup

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

	def find_all(
			self=None, name=None, attributes=None, text=None, in_spoon=True, soup=None, first_only=False,
			first_child=False, ignore_name=None, ignore_attributes=None
	):
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

		return self.filter(
			soup=soup, name=name, attributes=attributes, text=text, in_spoon=in_spoon, first_only=first_only,
			first_child=first_child, ignore_name=ignore_name, ignore_attributes=ignore_attributes
		)

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
		if isinstance(element, list):
			return element

		result = list(element.children)
		if result is None:
			raise RuntimeError('element does not have a children attribute!')
		elif len(result) == 0:
			return []
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

	def __add__(self, other):
		"""
		:type other: Spoon
		:rtype: Spoon
		"""

		soup1 = self.soup if isinstance(self.soup, list) else [self.soup]
		soup2 = other.soup if isinstance(other.soup, list) else [other.soup]
		return Spoon(soup=soup1 + soup2)

	@classmethod
	def _convert_to_list(cls, soup, extract_text=True, extract_tables=True, ignore_single_parents=False, keep_names=True, function=None, base_url=None):
		"""
		converts a BeautifulSoup or a Spoon full of BeautifulSoup into a list of lists/dictionaries
		:type soup: BeautifulSoup or Spoon
		:type extract_text: bool
		:type keep_names: bool
		:type function: callable
		:rtype: str or list[str] or list[list]
		"""

		if isinstance(soup, str) or soup is None:
			return soup
		elif isinstance(soup, list):
			if len(soup) == 1 and ignore_single_parents:
				return cls._convert_to_list(
					soup=soup[0], extract_text=extract_text, extract_tables=extract_tables,
					ignore_single_parents=ignore_single_parents,
					keep_names=keep_names, function=function, base_url=base_url
				)
			elif len(soup) > 0:
				return [
					cls._convert_to_list(
						soup=x,
						extract_text=extract_text,
						extract_tables=extract_tables,
						ignore_single_parents=ignore_single_parents,
						keep_names=keep_names,
						function=function,
						base_url=base_url
					)
					for x in soup if x is not None
				]
			else:
				return None
		elif isinstance(soup, Spoon):
			return cls._convert_to_list(
				soup=soup.soup,
				extract_text=extract_text,
				ignore_single_parents=ignore_single_parents,
				keep_names=keep_names,
				function=function
			)
		elif isinstance(soup, (BeautifulSoup, Tag, PageElement)):
			if soup.name == 'table' and extract_tables:
				result = read_tables(tables=soup, base_url=base_url)
				if keep_names:
					return {clean_name(soup=soup): result}
				else:
					return result

			elif len(Spoon.children(element=soup, in_spoon=False)) == 1 and ignore_single_parents:
				result = cls._convert_to_list(
					soup=Spoon.children(element=soup, in_spoon=False)[0],
					extract_text=extract_text,
					extract_tables=extract_tables,
					ignore_single_parents=ignore_single_parents,
					keep_names=keep_names,
					function=function,
					base_url=base_url
				)

				if keep_names:
					return {clean_name(soup=soup): result}
				else:
					return result

			elif len(Spoon.children(element=soup, in_spoon=False)) > 0:
				result = [
					cls._convert_to_list(
						soup=child,
						extract_text=extract_text,
						extract_tables=extract_tables,
						ignore_single_parents=ignore_single_parents,
						keep_names=keep_names,
						function=function,
						base_url=base_url
					)
					for child in Spoon.children(element=soup)
				]
				non_none = [x for x in result if x is not None]

				if keep_names:
					return {clean_name(soup=soup): non_none}
				else:
					return non_none

			else:
				if isinstance(soup, NavigableString):
					result = str(soup)
				elif extract_text or soup.name is None:
					result = str(soup.text)
				elif soup.name == 'a':
					result = parse_link(element=soup, base=base_url)
				else:
					result = soup

				if function is not None:
					result = function(result)

				if keep_names:
					return {clean_name(soup=soup): result}
				else:
					return result
		else:
			raise TypeError(f'cannot accept objects of type {type(soup)}')

	def convert_to_list(self=None, soup=None, extract_text=True, extract_tables=True, ignore_single_parents=False, keep_names=True, function=None, base_url=None, flatten=True):
		"""
		converts a BeautifulSoup or a Spoon full of BeautifulSoup into a list of lists/dictionaries
		:type soup: BeautifulSoup or Spoon or list[BeautifulSoup] or list[Spoon]
		:type extract_text: bool
		:type function: callable
		:rtype: str or list[str] or list[list]
		"""
		if self is None:
			result = Spoon._convert_to_list(
				soup=soup,
				extract_text=extract_text,
				extract_tables=extract_tables,
				ignore_single_parents=ignore_single_parents,
				keep_names=keep_names,
				function=function,
				base_url=base_url
			)
		else:

			result = self._convert_to_list(
				soup=soup or self,
				extract_text=extract_text,
				extract_tables=extract_tables,
				ignore_single_parents=ignore_single_parents,
				keep_names=keep_names,
				function=function,
				base_url=base_url
			)

		if flatten:
			return flatten_dictionaries_and_lists(result)
		else:
			return result

	def unwrap(self, name=None, attributes=None, smooth=False):
		parents = []
		for tag in self.find_all(name=name, attributes=attributes):
			tag.unwrap()
			if smooth and tag.parent is not None and tag.parent not in parents:
				parents.append(tag.parent)
		for tag in parents:
			tag.smooth()
		return self

	def remove(self, name=None, attributes=None):
		for tag in self.find_all(name=name, attributes=attributes):
			tag.extract()
		return self

	def clean_text(self):
		return self.unwrap(name='span', smooth=True).remove(name='br')

	def get_text(self, sep=' ', flatten=True):
		return get_text(tags=self.soup, sep=sep, flatten=flatten)
