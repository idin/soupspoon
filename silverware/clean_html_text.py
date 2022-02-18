from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from .clone_beautiful_soup_tag import clone_beautiful_soup_tag


def replace_images_with_text(element):
	"""
	replaces images with text
	:type element: BeautifulSoup or Tag or NavigableString
	:rtype: BeautifulSoup or Tag or NavigableString
	"""
	html = clone_beautiful_soup_tag(element)
	for elem in html.find_all('img'):
		if 'alt' in elem.attrs:
			elem.string_for_display = elem.attrs['alt']
	return html

def clean_html_text(html, replace_images=False):
	"""
	parses an html and either returns a string or None
	:type html: BeautifulSoup or Tag or NavigableString
	:type replace_images: bool
	:rtype: str or NoneType
	"""
	if isinstance(html, str):
		return html
	elif html is None:
		return None
	else:
		if replace_images:
			html = replace_images_with_text(element=html)
		text = html.get_text()
		return ' '.join(text.replace('\n', ' ').replace('\xa0', ' ').strip().split())
