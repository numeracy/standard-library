import csv
import operator
import os
import os.path

from util import SpaceTable, CsvTable, tidy_values

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
