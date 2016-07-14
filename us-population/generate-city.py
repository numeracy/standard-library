import csv
import operator
import re

from util import SpaceTable

exclude_regexes = [
	re.compile("(County|borough|Borough|urban county|unified government|\((pt\.|balance)\))$"),
	re.compile("^Balance of "),
	re.compile("government \(balance\)?$"),
]

common_names = {
	"Urban Honolulu CDP": "Honolulu",
	"Louisville/Jefferson County metro government": "Louisville",
	"Lynchburg, Moore County metropolitan government": "Lynchburg",
	"Butte-Silver Bow": "Butte",
	"Hartsville/Trousdale County": "Hartsville",
}

suffix_regex = re.compile(" (city|town|village|municipality|corporation|UT|CDP|comunidad|zona urbana)")

def canonical_name(name):
	remove_suffix = True

	if common_names.has_key(name):
		name = common_names[name]
		remove_suffix = False
	elif name.find("-") > 0 and re.search("(County|metropolitan government|urban county)", name):
		name = name[0:name.index("-")]
		remove_suffix = False

	should_exclude = False
	for exclude_regex in exclude_regexes:
		if exclude_regex.search(name):
			should_exclude = True
			break
	if should_exclude:
		print "excluding place: " + name
		return ""

	if remove_suffix:
		m = suffix_regex.search(name)
		if not m:
			print "suffix not found: " + name
		else:
			name = name[0:m.start()]
	return name


def generate_2015_data(outname):
	in_file = open("source-data/SUB-EST2015_ALL.csv")
	out_file = open("data/" + outname, "w+")

	reader = csv.DictReader(in_file)
	writer = csv.writer(out_file)

	writer.writerow(["City", "State", "Population"])

	for d in reader:
		if d["SUMLEV"] != "162" and d["SUMLEV"] != "170":
			continue # This is not a total place population

		name = canonical_name(d["NAME"])
		if not name:
			continue

		writer.writerow([name, d["STNAME"], d["POPESTIMATE2015"]])

def generate_2010_data(outname):
	in_file = open("source-data/sf1-place-pop.csv")
	out_file = open("data/" + outname, "w+")

	reader = csv.DictReader(in_file)
	writer = csv.writer(out_file)

	writer.writerow(["City", "State", "Population"])
	for d in reader:
		if not d.has_key("Place"):
			print "no place key: " + str(d)
			continue

		name = canonical_name(d["Place"])
		if not name:
			continue

		writer.writerow([name, d["State"], d["Population"]])

def city_data_90s():
	historical_values = []

	early_90s_info = {
		"table": SpaceTable("90-93", 19475, 0, [19477, 38928], in_thousands=False, ltrim=9),
		"year_indices": [("1990", -2), ("1991", -3), ("1992", -4), ("1993", -5)]
	}

	late_90s_info = {
		"table": SpaceTable("94-99", 13, 0, [15, 19466], in_thousands=False, ltrim=9),
		"year_indices": [("1994", -1), ("1995", -2), ("1996", -3), ("1997", -4), ("1998", -5), ("1999", -6)]
	}

	lines = open("source-data/SU-99-7_US.txt").readlines()

	for info in [early_90s_info, late_90s_info]:
		table_values = info["table"].table_values_for_lines(lines)[1]
		for i in range(1, len(table_values)):
			values = table_values[i]

			first_population_idx = 0
			for (idx, value) in enumerate(values):
				if re.match(r'\d+', value):
					first_population_idx = idx
					break
			if first_population_idx == 1:
				continue # this is a state

			state = values[first_population_idx-1]

			name = " ".join(values[0:first_population_idx-1])
			name = canonical_name(name)
			if not name:
				continue

			for (year, idx) in info["year_indices"]:
				historical_values.append([name, state, year, values[idx]])

	return historical_values

def generate_historical(outname):
	historical_values = city_data_90s()

	info_2000s = {
		"filename": "SUB-EST00INT-Cities.csv",
		"year_range": (2000, 2010)
	}
	info_2010s = {
		"filename": "SUB-EST2015_ALL.csv",
		"year_range": (2010, 2016)
	}

	for info in [info_2000s, info_2010s]:
		reader = csv.DictReader(open("source-data/" + info["filename"]))

		for d in reader:
			if not d.has_key("SUMLEV") or (d["SUMLEV"] != "162" and d["SUMLEV"] != "170"):
				continue # This is not a total place population

			name = canonical_name(d["NAME"])
			if not name:
				continue

			state = d["STNAME"]

			for year in range(*info["year_range"]):
				population = d["POPESTIMATE" + str(year)]
				historical_values.append([name, state, str(year), population])


	historical_values.sort(key=operator.itemgetter(1, 0, 2))

	out_file = open("data/" + outname, "w+")
	writer = csv.writer(out_file)
	writer.writerow(["City","State","Year","Population"])
	writer.writerows(historical_values)

if __name__ == "__main__":
	generate_2010_data("city-census.csv")
	generate_2015_data("city-latest.csv")
	generate_historical("cities.csv")