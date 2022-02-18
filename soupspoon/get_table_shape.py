import copy

def _get_table_shape(table):
	num_rows = 0
	num_header_rows = 0
	max_num_columns = 0

	inside_header = True
	for row in table.find_all("tr"):
		if inside_header:
			inside_header = row.find('td') is None

		# Skip row if it's blank
		columns = row.find_all(["td", "th"])
		num_columns_in_row = 0
		max_num_row_spans = 0
		if len(columns) > 0:
			for col in columns:
				colspan = col.get("colspan")
				if colspan is None:
					num_col_spans = 1
				else:
					num_col_spans = int(colspan)
				num_columns_in_row += num_col_spans

				rowspan = col.get("rowspan")
				if rowspan is None:
					num_row_spans = 1
				else:
					num_row_spans = int(rowspan)
				max_num_row_spans = max(max_num_row_spans, num_row_spans)

		if inside_header:
			num_header_rows += max_num_row_spans
		else:
			num_rows += max_num_row_spans

		max_num_columns = max(max_num_columns, num_columns_in_row)

	return {'num_header_rows': num_header_rows, 'num_rows': num_rows, 'num_columns': max_num_columns}


def get_table_shape(table):
	# Create list to store rowspan values
	skip_index = []
	this_skip_index = []

	# Start by iterating over each row in this table...
	row_counter = 0
	header_row_counter = 0
	max_num_rows = 0
	max_num_header_rows = 0
	max_num_columns = 0
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

				# Insert data into cell all cells of a merged cell
				if colspan is None:
					num_columns_in_cell = 1
				else:
					num_columns_in_cell = int(colspan)

				if rowspan is None:
					num_rows_in_cell = 1
				else:
					num_rows_in_cell = int(rowspan)

				max_num_columns = max(max_num_columns, col_counter + num_columns_in_cell)
				if is_header:
					max_num_header_rows = max(max_num_header_rows, header_row_counter + num_rows_in_cell)
				else:
					max_num_rows = max(max_num_rows, row_counter + num_rows_in_cell)

				# Record column skipping index
				if row_dim[row_dim_counter] > 1:
					if col_counter < len(this_skip_index):
						this_skip_index[col_counter] = row_dim[row_dim_counter]


		# Adjust row counter
		if is_header:
			header_row_counter += 1
		else:
			row_counter += 1

		# Adjust column skipping index
		skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

	return {'num_header_rows': max_num_header_rows, 'num_rows': max_num_rows, 'num_columns': max_num_columns}
