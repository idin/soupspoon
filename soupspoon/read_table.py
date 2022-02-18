import pandas as pd
import copy
from collections import Counter
from bs4 import BeautifulSoup, Tag
import warnings

from .clone_beautiful_soup_tag import clone_beautiful_soup_tag
from .clean_html_text import clean_html_text
from .find_links import find_links
from .get_table_shape import get_table_shape

def add_to_dataframe(dataframe, row, column, value):
	num_rows = dataframe.shape[0]
	num_columns = dataframe.shape[1]
	for i in range(row + 1 - num_rows):
		dataframe = dataframe.append(pd.Series(name=i+num_rows), ignore_index=False)
	for j in range(column + 1 - num_columns):
		dataframe[j+num_columns] = None
	dataframe.iat[row, column] = value
	return dataframe

'''
def get_table_shape(table):
	num_columns = 0
	num_header_rows = 0
	num_rows = 0

	is_header = True
	for row in table.find_all("tr"):
		columns = row.find_all(["td", "th"])
		if len(columns) > 0:

			if is_header:
				if row.find('td') is None:
					num_header_rows += 1

				else:
					is_header = False
					num_rows += 1

			else:
				num_rows += 1

			if len(columns) > num_columns:
				num_columns = len(columns)
	return {'num_header_rows': num_header_rows, 'num_rows': num_rows, 'num_columns': num_columns}
'''


def join_html_texts(texts):
	string = ' '.join([text for text in texts if isinstance(text, str)])
	return clean_html_text(string)


def read_table(table, parse_links=False, base_url=None):
	table = clone_beautiful_soup_tag(table)
	for elem in table.find_all(["br"]):
		elem.replace_with(elem.text + "\n")

	table_shape = get_table_shape(table=table)

	# Create dataframe
	dataframe = pd.DataFrame(index=range(0, table_shape['num_rows']), columns=range(0, table_shape['num_columns']))
	header = pd.DataFrame(index=range(0, table_shape['num_header_rows']), columns=range(0, table_shape['num_columns']))

	# Create list to store rowspan values
	skip_index = [0 for _ in range(0, table_shape['num_columns'])]

	# Start by iterating over each row in this table...
	row_counter = 0
	header_row_counter = 0

	is_header = True
	for row in table.find_all("tr"):
		if is_header:
			is_header = row.find('td') is None

		# Skip row if it's blank
		columns = row.find_all(["td", "th"])
		if len(columns) > 0:
			# Get all cells containing data in this row

			col_dim = []
			row_dim = []
			col_dim_counter = -1
			row_dim_counter = -1
			col_counter = -1
			this_skip_index = copy.deepcopy(skip_index)

			for col in columns:

				# Determine cell dimensions
				colspan = col.get("colspan")
				if colspan is None:
					col_dim.append(1)
				else:
					col_dim.append(int(colspan))
				col_dim_counter += 1

				rowspan = col.get("rowspan")
				if rowspan is None:
					row_dim.append(1)
				else:
					row_dim.append(int(rowspan))
				row_dim_counter += 1

				# Adjust column counter
				if col_counter == -1:
					col_counter = 0
				else:
					col_counter = col_counter + col_dim[col_dim_counter - 1]

				while col_counter < len(this_skip_index) and this_skip_index[col_counter] > 0:
					col_counter += 1

				# Get cell contents
				if is_header:
					cell_data = clean_html_text(col, replace_images=True)
				elif parse_links:
					links = find_links(elements=col, base=base_url)
					if len(links) == 0:
						cell_data = clean_html_text(col, replace_images=True)
					elif len(links) == 1:
						cell_data = links[0]
					else:
						cell_data = links
				else:
					cell_data = clean_html_text(col, replace_images=True)


				# Insert data into cell all cells of a merged cell
				if colspan is None:
					num_columns_in_cell = 1
				else:
					num_columns_in_cell = int(colspan)

				if rowspan is None:
					num_rows_in_cell = 1
				else:
					num_rows_in_cell = int(rowspan)

				if is_header:
					for row_num in range(num_rows_in_cell):
						for column_num in range(num_columns_in_cell):
							header = add_to_dataframe(
								dataframe=header, row=header_row_counter + row_num, column=col_counter + column_num, value=cell_data
							)

				else:
					for row_num in range(num_rows_in_cell):
						for column_num in range(num_columns_in_cell):
							dataframe = add_to_dataframe(
								dataframe=dataframe, row=row_counter + row_num, column=col_counter + column_num, value=cell_data
							)

				# Record column skipping index
				if row_dim[row_dim_counter] > 1:
					this_skip_index[col_counter] = row_dim[row_dim_counter]

		# Adjust row counter
		if is_header:
			header_row_counter += 1
		else:
			row_counter += 1

		# Adjust column skipping index
		skip_index = [i - 1 if i > 0 else i for i in this_skip_index]
	columns = [join_html_texts(header[col].values) for col in header.columns]
	column_name_counter = Counter(columns)
	columns_with_number = []
	column_numbers = {}
	for column in columns:
		if column_name_counter[column] > 1:
			if column in column_numbers:
				column_numbers[column] += 1
			else:
				column_numbers[column] = 1
			columns_with_number.append(f'{column} {column_numbers[column]}')
		else:
			columns_with_number.append(column)

	dataframe.columns = columns_with_number
	return dataframe.reset_index(drop=True)


def read_tables(tables, parse_links=False, base_url=None, if_error='ignore'):
	if isinstance(tables, (BeautifulSoup, Tag)):
		try:
			return read_table(table=tables, parse_links=parse_links, base_url=base_url)
		except Exception as e:
			if if_error == 'ignore':
				return None
			elif if_error.startswith('warn'):
				warnings.warn(str(e))
			else:
				raise e

	else:
		result = [
			read_tables(tables=table, parse_links=parse_links, base_url=base_url, if_error=if_error)
			for table in tables
		]
		return [x for x in result if x is not None]
