from pandas import DataFrame
from pandas.api.types import is_numeric_dtype

from .BaseHtmlText import BaseHtmlText
from .StructuredText import StructuredText


class HtmlText(BaseHtmlText):
	def __init__(self, obj, extract_tags=False, ignore_function=None, log=False, num_jobs=1):
		super().__init__(
			obj=obj,
			extract_tags=extract_tags,
			_id='1',
			ignore_function=ignore_function,
			depth=0,
			ids=None,
			log=log,
			num_jobs=num_jobs
		)
		self._data = None
		self._font_sizes = None
		self._full_data = None
		self._font_size_data = {}

	@classmethod
	def _get_state_attribute_names(cls):
		super_attribute_names = super()._get_state_attribute_names()
		other_attribute_names = {
			'_data': None,
			'_font_size_data': {},
			'_font_sizes': None,
			'_full_data': None,
			'_logs': [],
			'_ids': {}
		}
		return {**super_attribute_names, **other_attribute_names}

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._set_logs(logs=self._logs)
		self._set_ids(ids=self._ids)

	def __getstate__(self):
		state = super().__getstate__()
		return state

	@property
	def data(self):
		"""
		produces a data file of all the texts
		:rtype: DataFrame
		"""
		if self._data is None:
			self._data = DataFrame.from_records(self.records)
		return self._data

	@property
	def font_size_data(self):
		"""
		produces an aggregate data of font sizes
		:rtype: DataFrame
		"""
		return self.get_font_size_data()

	def get_font_size_data(self, split_by_weight=False):
		"""
		produces an aggregate data of font sizes
		:rtype: DataFrame
		"""
		key = (split_by_weight)
		if self._font_size_data is None:
			self._font_size_data = {}
		if key not in self._font_size_data:
			possible_group_columns = ['font_family', 'font_size']
			if split_by_weight:
				possible_group_columns = ['font_weight'] + possible_group_columns

			group_columns = [col for col in possible_group_columns if col in self.data.columns]
			data = self.data[['num_characters', 'num_strings'] + group_columns].copy()
			data['count'] = 1

			df = data.groupby(by=group_columns).agg(['median', 'sum']).reset_index(drop=False)

			df.columns = df.columns.map(lambda x: '_'.join(x).strip('_'))
			df['character_to_string_ratio'] = df['num_characters_sum'] / df['num_strings_sum']
			self._font_size_data[key] = df.rename(columns={'count_sum': 'count'}).drop(columns=['count_median'])
		return self._font_size_data[key]

	@property
	def font_sizes(self):
		"""
		:rtype: int or float
		"""

		if self._font_sizes is None:
			df = self.get_font_size_data()
			# body font size is the one with the largest character to string ratio
			max_character_to_string_ratio = df.character_to_string_ratio.max()

			body_font_size = df[df.character_to_string_ratio == max_character_to_string_ratio].iloc[0]['font_size']

			# title font sizes are the ones larger than body
			title_font_sizes = list(df[df.font_size > body_font_size]['font_size'])
			self._font_sizes = {'body': body_font_size, 'title_min': min(title_font_sizes), 'titles': title_font_sizes}
		return self._font_sizes

	@property
	def structured_text(self):
		"""
		:rtype: StructuredText
		"""
		return StructuredText(html_text=self)

	@property
	def full_data(self):
		"""
		:rtype: DataFrame
		"""
		if self._full_data is None:
			self._full_data = self.data.merge(right=self.get_font_size_data())
		return self._full_data

	def display_statistics(self):
		max_column_length = max([len(str(column)) for column in self.full_data.columns])
		result = []
		for column in self.full_data.columns:
			c = str(column)
			if is_numeric_dtype(self.full_data[column]):
				_min = round(self.full_data[column].min(), 2)
				_max = round(self.full_data[column].max(), 2)
				_median = round(self.full_data[column].median(), 2)
				_mean = round(self.full_data[column].mean(), 2)

				result.append(
					f'{c.ljust(max_column_length)} - min: {_min}, max: {_max}, mean: {_mean}, median: {_median}'
				)

			else:
				most_common = '", "'.join(self.full_data[column].value_counts()[:5].index.tolist())

				result.append(
					f'{c.ljust(max_column_length)} - common values: "{most_common}"'
				)
		print('\n'.join(result))

	def filter(self, dictionary, break_lines=True):
		"""
		returns a list of strings with the texts that fit the criteria in the dictionary
		:param dict dictionary: a dictionary that provides instructions about how to filter the data
		:rtype: list[str]
		"""
		result = self.full_data
		for key, value in dictionary.items():
			if isinstance(value, str) and value.startswith(('<', '>', '=', '!=')):

				if value.startswith(('>=', '<=', '!=', '==')):
					actual_value = value[2:].lstrip()
					if is_numeric_dtype(result[key]):
						actual_value = float(actual_value)

					if value.startswith('>='):
						result = result[result[key] >= actual_value]

					elif value.startswith('<='):
						result = result[result[key] <= actual_value]

					elif value.startswith('!='):
						result = result[result[key] != actual_value]

					elif value.startswith('=='):
						result = result[result[key] == actual_value]

				elif value.startswith(('>', '<', '=')):
					actual_value = value[1:].lstrip()
					if is_numeric_dtype(result[key]):
						actual_value = float(actual_value)

					if value.startswith('='):
						result = result[result[key] == actual_value]

					elif value.startswith('<'):
						result = result[result[key] < actual_value]

					elif value.startswith('>'):
						result = result[result[key] > actual_value]

			else:
				result = result[result[key] == value]

		if break_lines:
			return [y for x in list(result.text) for y in x.split('\n')]

		else:
			return list(result.text)
