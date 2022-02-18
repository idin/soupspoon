def clean_name(soup):
	name = soup.name
	if isinstance(name, (list, tuple)) and len(name) == 1:
		return name[0]

	brackets = [('[', ']'), ('(', ')'), ('{', '}')]
	while any(name.startswith(x) and name.endswith(y) for x, y in brackets):
		name = name[1:-1]
	return name
