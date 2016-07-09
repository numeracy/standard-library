import csv
import re

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


if __name__ == "__main__":
	generate_2010_data("city-census.csv")
	generate_2015_data("city-latest.csv")