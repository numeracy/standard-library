import csv
import operator
import os
import os.path
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

		us_values = [headers]
		state_values = [headers]

		us_row = self.row_for_line(lines[self.us_row - 1])
		us_values.append(self.population_values_for_row(us_row))

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

table_defs = {
	"st0009ts.txt": [SpaceTable("00-05", 16, 18, (24, 73)), SpaceTable("06-09", 74, 76, (82, 131))],
	"st1019ts.txt": [SpaceTable("10-15", 16, 18, (24, 73)), SpaceTable("16-19", 74, 76, (82, 131))],
	"st2029ts.txt": [SpaceTable("20-25", 16, 18, (24, 73)), SpaceTable("26-29", 74, 76, (82, 131))],
	"st3039ts.txt": [SpaceTable("30-35", 16, 18, (24, 73)), SpaceTable("36-39", 75, 77, (83, 132))],
	"st4049ts.txt": [SpaceTable("40-45", 14, 16, (22, 71)), SpaceTable("46-49", 72, 74, (80, 129))],
	"st5060ts.txt": [
		SpaceTable("50-54", 17, 19, (28, 79), skip_col=1),
		SpaceTable("55-59", 82, 84, (93, 144), skip_col=6)
	],
	"st6070ts.txt": [
		SpaceTable("60-64", 17, 19, (25, 76), skip_col=1),
		SpaceTable("65-69", 79, 81, (87, 138), skip_col=6)
	],
	"st7080ts.txt": [
		SpaceTable("70-75", 14, 66, (15, 66), skip_col=0, in_thousands=False),
		SpaceTable("76-79", 67, 119, (68, 119), skip_col=0, in_thousands=False)
	],
	"st8090ts.txt": [
		SpaceTable("80-84", 10, 11, (12, 63), in_thousands=False),
		SpaceTable("85-89", 69, 70, (71, 122), skip_col=6, in_thousands=False)
	],
	"ST-99-03.txt": [
		SpaceTable("90-93", 84, 88, (102, 153), ltrim=7, skip_col=5, in_thousands=False),
		SpaceTable("94-99", 10, 14, (28, 79), ltrim=7, in_thousands=False)
	],
	"ST-EST00INT-01.csv": [CsvTable("2000-2009", 4, 5, (10, 61), 0, (3, 12))],
	"NST-EST2015-alldata.csv": [CsvTable("2010-2015", 1, 2, (7, 58), 4, (7, 13))]
}

def process_file(filename):
	lines = open("source-data/" + filename).readlines()
	tidied_us_values = []
	tidied_state_values = []
	for table in table_defs[filename]:
		us_values, state_values = table.table_values_for_lines(lines)
		tidied_us_values.extend(tidy_values(us_values))
		tidied_state_values.extend(tidy_values(state_values))

	return tidied_us_values, tidied_state_values

def process_all():
	us_file = open("data/us-population.csv", "w+")
	us_writer = csv.writer(us_file)

	state_file = open("data/state-populations.csv", "w+")
	state_writer = csv.writer(state_file)

	us_writer.writerow(["Year", "Population"])
	state_writer.writerow(["State", "Year", "Population"])

	us_values = []
	state_values = []

	for filename in os.listdir("source-data"):
		if table_defs.has_key(filename):
			table_us_values, table_state_values = process_file(filename)
			us_values.extend(table_us_values)
			state_values.extend(table_state_values)

	us_values.sort(key=operator.itemgetter(1), reverse=True)
	for row in us_values:
		us_writer.writerow(row[1:])

	state_values.sort(key=lambda d: [d[0], 3000-int(d[1])])
	state_writer.writerows(state_values)

	us_file.close()
	state_file.close()

if __name__ == "__main__":
	process_all()
