from pandas import DataFrame, concat
from .get_text_and_depth import get_text_and_depth


def get_html_text(tag, simplify_ids=True):
	"""
	:type tag:
	:type simplify_ids: bool
	:rtype: DataFrame
	"""
	records = get_text_and_depth(tag=tag, id='', parent_id=None, depth=0, parent_style={})

	result = DataFrame.from_records(records)
	if 'font_weight' in result.columns:
		result['is_bold'] = result['font_weight'].fillna('normal').str.lower() == 'bold'
	else:
		result['is_bold'] = False

	if 'font_style' in result.columns:
		result['is_italic'] = result['font_style'].fillna('normal').str.lower() == 'italic'
	else:
		result['is_italic'] = False

	columns_to_drop = [
		'position', 'border', 'left', 'top', 'width', 'height', 'writing_mode', 'font_weight', 'font_style'
	]
	result.drop(columns=[col for col in columns_to_drop if col in result.columns], inplace=True)

	# add number of siblings
	parents = result[['parent_id']].copy()
	parents['count'] = 1
	num_children_data = parents.groupby('parent_id').sum().reset_index()
	num_children_data.rename(columns={'count': 'num_siblings'}, inplace=True)
	num_children_data['num_siblings'] = num_children_data['num_siblings'] - 1
	result = result.merge(num_children_data, on='parent_id', how='left')

	# get child index
	def add_index(x):
		x = x.copy()
		x['child_index'] = range(x.shape[0])
		return x

	grouped = result.groupby('parent_id')
	result['index'] = range(result.shape[0])
	result = concat([add_index(data) for _, data in grouped]).sort_values(['parent_id', 'index']).reset_index(drop=True)

	if simplify_ids:
		id_counter = 0

		id_dictionary = {}
		for id in list(result['parent_id']) + list(result['id']):
			if id not in id_dictionary:
				id_dictionary[id] = id_counter
				id_counter += 1

		def simplify_id(x):
			return id_dictionary[x]

		result['id'] = result['id'].apply(simplify_id)
		result['parent_id'] = result['parent_id'].apply(simplify_id)

	return result
