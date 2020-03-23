from disk import Path
from bs4 import BeautifulSoup


from .Spoon import Spoon


class HtmlFile(Path):
	def __init__(self, string, show_size=False):
		super().__init__(string=string, show_size=show_size)
		self._soup = None

	@property
	def soup(self):
		"""
		:rtype: BeautifulSoup
		"""
		if self._soup is None:
			self._soup = BeautifulSoup('\n'.join(self.read_lines()), 'lxml')
		return self._soup

	@property
	def spoon(self):
		"""
		:rtype: Spoon
		"""
		return Spoon(soup=self.soup)
