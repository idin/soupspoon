import re


def get_font_size(tag):
	try:
		style = tag.attrs.get('style')
		font_size = re.search(r'(?is)(font-size:)(.*?)(px)', str(style)).group(2)
		return float(font_size)
	except AttributeError:
		return None


FONT_WEIGHTS = {
	'bold': 'bold',
	'bolditalic': 'bold',
	'boldoblique': 'bold'
}

FONT_STYLES = {
	'italic': 'italic',
	'oblique': 'oblique',
	'bolditalic': 'italic',
	'boldoblique': 'oblique'
}


def get_style(tag):
	try:
		style = tag.attrs.get('style')
		result = {}
		for s in str(style).split(';'):
			key_value = s.split(':')
			if len(key_value) == 2:
				key, value = key_value
				key = key.strip().replace('-', '_').lower()
				value = value.strip()
				if value.endswith('px'):
					value = int(value[:-2])

				if key == 'font_family':
					words = [x.strip().lower() for x in value.split(',')]

					for key, weight in FONT_WEIGHTS.items():
						if key in words:
							result['font_weight'] = weight
							break
					else:
						result['font_weight'] = 'normal'

					for key, style in FONT_STYLES.items():
						if key in words:
							result['font_style'] = style
							break
					else:
						result['font_style'] = 'normal'

					result['font_family'] = ';'.join([
						word for word in words
						if word not in FONT_WEIGHTS and word not in FONT_STYLES
					])

				else:
					result[key] = value
		if 'font_size' not in result:
			font_size = get_font_size(tag)
			if font_size is not None:
				result['font_size'] = font_size
		return result

	except AttributeError:
		return {}
