import csv
import re

value_regex = re.compile('((New|North|South|West|Rhode|District of|United) \S+|\S+)')
number_regex = re.compile('\d+')
short_date_regex = re.compile('(\d+/)?\d+/(\d+)')

state_name_for_abbrev = {}
abbrev_reader = csv.DictReader(open("source-data/state-abbreviations.csv"))
for state in abbrev_reader:
	state_name_for_abbrev[state["USPS"]] = state["Name"]

def normalize_value(value):
	if value and value[0] == ".":
		value = value[1:]
	
	if state_name_for_abbrev.has_key(value):
		value = state_name_for_abbrev[value]
	elif value.find("POPESTIMATE") == 0:
		value = value[len("POPESTIMATE"):]
	return value.replace(",", "")

def normalize_years(header_row):
	for i in range(len(header_row)):
		m = short_date_regex.match(header_row[i])
		if m:
			header_row[i] = "19" + m.group(2)

def tidy_values(table_values):
	tidied_values = []

	header_row = table_values[0]
	for i in range(1, len(table_values)):
		row = table_values[i]

		state = row[0]
		for j in range(1, len(row)):
			try: # XXX
				year = header_row[j]
			except:
				print "j: %d\nrow: %s\ntable_values: %s" % (j, row, table_values)
			population = row[j]
			tidied_values.append([state, year, population])

	return tidied_values

class SpaceTable(object):
	def __init__(self, name, header_row, us_row, row_range, in_thousands=True, ltrim=0, skip_col=None):
		self.name = name
		self.header_row = header_row
		self.us_row = us_row
		self.row_range = row_range
		self.in_thousands = in_thousands
		self.ltrim = ltrim
		self.skip_col = skip_col

	def remove_skipped(self, values):
		if self.skip_col is not None:
			values.pop(self.skip_col)

	def row_for_line(self, line):
		if self.ltrim == 0:
			return line
		else:
			return line[self.ltrim:]

	def values_for_row(self, row):
		return [normalize_value(match[0]) for match in value_regex.findall(row)]

	def population_values_for_row(self, row):
		values = self.values_for_row(row)
		self.remove_skipped(values)
		if self.in_thousands:
			for val_idx in range(1, len(values)):
				int_val = int(values[val_idx])
				int_val *= 1000
				values[val_idx] = str(int_val)
		return values

	def table_values_for_lines(self, lines):
		header_row = self.row_for_line(lines[self.header_row - 1])
		headers = []
		if header_row[0] == " ":
			headers.append("State")
		headers.extend(self.values_for_row(header_row))
		self.remove_skipped(headers)
		normalize_years(headers)

		us_values = []
		if self.us_row > 0:
			us_values.append(headers)
			us_row = self.row_for_line(lines[self.us_row - 1])
			us_values.append(self.population_values_for_row(us_row))

		state_values = [headers]
		for i in range (self.row_range[0] - 1, self.row_range[1] - 1):
			row = self.row_for_line(lines[i])
			state_values.append(self.population_values_for_row(row))

		return (us_values, state_values)

class CsvTable(object):
	def __init__(self, name, header_row, us_row, row_range, state_col, col_range):
		self.name = name
		self.header_row = header_row
		self.us_row = us_row
		self.row_range = row_range
		self.state_col = state_col
		self.col_range = col_range

	def values_for_row(self, row):
		state_value = row[self.state_col]
		values = [normalize_value(state_value)]

		for j in range(*self.col_range):
			value = row[j]
			values.append(normalize_value(value))

		return values

	def table_values_for_lines(self, lines):
		r = csv.reader(lines)
		rows = []
		for row in r:
			rows.append(map(normalize_value, row))

		header_row = self.values_for_row(rows[self.header_row-1])
		if not header_row[0]:
			header_row[0] = "State"
		us_values = [header_row]
		state_values = [header_row]

		us_values.append(self.values_for_row(rows[self.us_row - 1]))

		for i in range(self.row_range[0]-1, self.row_range[1]-1):
			values = self.values_for_row(rows[i])
			state_values.append(values)

		return (us_values, state_values)
