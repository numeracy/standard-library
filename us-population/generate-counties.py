import codecs
import csv
import operator
import util
import re

from cStringIO import StringIO

def include_2010_to_2020(rows):
	reader = csv.DictReader(open("source-data/PEP_2015_PEPANNRES_with_ann.csv"))
	fields = [("2010", "respop72010"), ("2011", "respop72011"), ("2012", "respop72012"),
			("2013", "respop72013"), ("2014", "respop72014"), ("2015", "respop72015")]
	for row in reader:
		fips = row["GEO.id2"]
		state = util.postal_code_for_fips[fips[0:2]]
		for (year, field_name) in fields:
			population = row[field_name]
			rows.append([state, fips, year, population])

suffix_regex = re.compile(" city$")

def canonicalize_county_name(name):
	suffix_match = suffix_regex.search(name)
	if suffix_match:
		name = name[0:suffix_match.start()]
	return name

def include_2000_to_2009(rows):
	fips_by_state_name = {}
	county_abbreviations_ascii = codecs.open("source-data/county-abbreviations.csv", "r", "utf-8").read().encode("utf-8")
	for county in csv.DictReader(StringIO(county_abbreviations_ascii)):
		key = county["State"] + "-" + county["County"]
		fips_by_state_name[key] = county["FIPS"]

	for state in csv.DictReader(open("source-data/state-abbreviations.csv")):
		postal_code = state["Postal Code"]

		source_url = "source-data/counties-2000-2010/%s.csv" % postal_code
		for (idx, county_row) in enumerate(csv.reader(open(source_url))):
			if idx < 5 or len(county_row) == 0:
				continue
			county_name = county_row[0]
			if county_name[0] != ".":
				continue
			county_name = county_name[1:].decode("latin-1")
			county_name = canonicalize_county_name(county_name).encode("utf-8")

			fips_key = postal_code + "-" + county_name
			fips = fips_by_state_name[fips_key]

			for col_idx in range(2, 12):
				year = str(1998 + col_idx)
				population = county_row[col_idx].replace(",", "")
				rows.append([postal_code, fips, year, population])

def include_1970_to_1999(rows):
	for county in csv.DictReader(open("source-data/county_population.csv")):
		if county["county_fips"] == "0" or (not county["pop1970"] and not county["pop1999"]):
			continue

		fips = "%05d" % int(county["fips"])
		state = util.postal_code_for_fips[fips[0:2]]

		for year in range(1970, 2000):
			population = county["pop%s" % year]
			if not population:
				print "Data not found for county %s" % county["county_name"]
				continue

			rows.append([state, fips, str(year), population])


def generate_counties():
	rows = []

	include_2010_to_2020(rows)
	include_2000_to_2009(rows)
	include_1970_to_1999(rows)

	rows.sort(key=operator.itemgetter(1, 2))

	outfile = open("data/counties.csv", "w+")
	writer = csv.writer(outfile)
	writer.writerow(["State", "FIPS", "Year", "Population"])
	writer.writerows(rows)
	outfile.close()

if __name__ == "__main__":
	generate_counties()