import census
import csv

c = census.Census("d0aed3790c96f4f43bc7e37bbddae0e55c56ee01")

aggregation_fields = {
	"zip": "zip code tabulation area",
}

fields = {
	"population": "B01003_001E",

	"edu_divisor": "B15003_001E",
	"edu_high_school": "B15003_017E",
	"edu_ged": "B15003_018E",
	"edu_year_of_college": "B15003_019E",
	"edu_years_of_college": "B15003_020E",
	"edu_assoc": "B15003_021E",
	"edu_bach": "B15003_022E",
	"edu_mast": "B15003_023E",
	"edu_professional": "B15003_024E",
	"edu_doctorate": "B15003_025E",

	"race_total": "B03002_001E",
	"race_white_nonhisp": "B03002_003E",
	"race_black_nonhisp": "B03002_004E",
	"race_native_nonhisp": "B03002_005E",
	"race_asian_nonhisp": "B03002_006E",
	"race_pacific_nonhisp": "B03002_007E",
	"race_other_nonhisp": "B03002_008E",
	"race_multi_nonhisp": "B03002_009E",
	"hispanic_total": "B03002_012E",

	"age_total": "B01001_001E",

	"male_under5": "B01001_003E",
	"male_5_to_9": "B01001_004E",
	"male_10_to_14": "B01001_005E",
	"male_15_to_17": "B01001_006E",
	"male_18_to_19": "B01001_007E",
	"male_20": "B01001_008E",
	"male_21": "B01001_009E",
	"male_22_to_24": "B01001_010E",
	"male_25_to_29": "B01001_011E",
	"male_30_to_34": "B01001_012E",
	"male_35_to_39": "B01001_013E",
	"male_40_to_44": "B01001_014E",
	"male_45_to_49": "B01001_015E",
	"male_50_to_54": "B01001_016E",
	"male_55_to_59": "B01001_017E",
	"male_60_to_61": "B01001_018E",
	"male_62_to_64": "B01001_019E",
	"male_65_to_66": "B01001_020E",
	"male_67_to_69": "B01001_021E",
	"male_70_to_74": "B01001_022E",
	"male_75_to_79": "B01001_023E",
	"male_80_to_84": "B01001_024E",
	"male_85_plus": "B01001_025E",

	"female_under5": "B01001_027E",
	"female_5_to_9": "B01001_028E",
	"female_10_to_14": "B01001_029E",
	"female_15_to_17": "B01001_030E",
	"female_18_to_19": "B01001_031E",
	"female_20": "B01001_032E",
	"female_21": "B01001_033E",
	"female_22_to_24": "B01001_034E",
	"female_25_to_29": "B01001_035E",
	"female_30_to_34": "B01001_036E",
	"female_35_to_39": "B01001_037E",
	"female_40_to_44": "B01001_038E",
	"female_45_to_49": "B01001_039E",
	"female_50_to_54": "B01001_040E",
	"female_55_to_59": "B01001_041E",
	"female_60_to_61": "B01001_042E",
	"female_62_to_64": "B01001_043E",
	"female_65_to_66": "B01001_044E",
	"female_67_to_69": "B01001_045E",
	"female_70_to_74": "B01001_046E",
	"female_75_to_79": "B01001_047E",
	"female_80_to_84": "B01001_048E",
	"female_85_plus": "B01001_049E",

	"per_capita_income": "B19301_001E",
	"median_household_income": "B19013_001E",

	"household_income_total": "B19001_001E",
	"household_below_10": "B19001_002E",
	"household_10_to_15": "B19001_003E",
	"household_15_to_20": "B19001_004E",
	"household_20_to_25": "B19001_005E",
	"household_25_to_30": "B19001_006E",
	"household_30_to_35": "B19001_007E",
	"household_35_to_40": "B19001_008E",
	"household_40_to_45": "B19001_009E",
	"household_45_to_50": "B19001_010E",
	"household_50_to_60": "B19001_011E",
	"household_60_to_75": "B19001_012E",
	"household_75_to_100": "B19001_013E",
	"household_100_to_125": "B19001_014E",
	"household_125_to_150": "B19001_015E",
	"household_150_to_200": "B19001_016E",
	"household_200_plus": "B19001_017E",
}

def fetch_values(fetcher, values):
	results = None
	while values:
		subres = fetcher(values[:50])
		values = values[50:]
		if results == None:
			results = subres
		else:
			for i, result in enumerate(results):
				result.update(subres[i])
	return results

def process_results(results, primary_key):
	processed = [
		[primary_key, "population",
		 "high_school", "bachelors", "graduate",
		 "white", "black", "native", "asian", "hispanic", "other",
		 "0_to_17", "18_to_24", "25_to_49", "45_to_64", "65_plus",
		 "per_capita_income", "median_household_income",
		 "$0_to_50k", "$50_to_100k", "$100_to_200", "$200_plus"]
	]
	census_primary_key = aggregation_fields[primary_key]

	for result in results:
		def getter(field):
			census_key = fields[field]
			return result[census_key]

		def get_float(field):
			val = getter(field)
			if val is None:
				return 0
			elif isinstance(val, str) or isinstance(val, unicode):
				return float(val)
			else:
				print "Unknown type %s: %s" % (type(val), val)
				return 0

		edu_divisor = get_float("edu_divisor")

		def calculate_edu_percent(count):
			if edu_divisor == 0:
				return "0"
			else:
				return str(count / edu_divisor)

		doc_or_professional = get_float("edu_professional") + get_float("edu_doctorate")
		at_least_bach = doc_or_professional + get_float("edu_bach") + get_float("edu_mast")
		at_least_high_school = at_least_bach + get_float("edu_high_school") + get_float("edu_ged") + \
			get_float("edu_year_of_college") + get_float("edu_years_of_college") + get_float("edu_assoc")

		race_total = get_float("race_total")

		def get_race_percent(fields):
			if race_total == 0:
				return "0"
			total = 0
			for field in fields:
				total += get_float(field)
			return total / race_total

		age_total = get_float("age_total")

		def get_age_percent(fields):
			if age_total == 0:
				return "0"
			total = 0
			for field in fields:
				total += get_float("male_" + field)
				total += get_float("female_" + field)
			return str(total / age_total)

		household_income_total = get_float("household_income_total")

		def get_household_percent(fields):
			if household_income_total == 0:
				return "0"
			total = 0
			for field in fields:
				total += get_float(field)
			return str(total / household_income_total)

		processed.append([
			result[census_primary_key],
			get_float("population"),

			# education
			calculate_edu_percent(at_least_high_school),
			calculate_edu_percent(at_least_bach),
			calculate_edu_percent(doc_or_professional),

			# race
			get_race_percent(["race_white_nonhisp"]),
			get_race_percent(["race_black_nonhisp"]),
			get_race_percent(["race_native_nonhisp"]),
			get_race_percent(["race_asian_nonhisp", "race_pacific_nonhisp"]),
			get_race_percent(["hispanic_total"]),
			get_race_percent(["race_other_nonhisp", "race_multi_nonhisp"]),

			# age
			get_age_percent(["under5", "5_to_9", "10_to_14", "15_to_17"]),
			get_age_percent(["18_to_19", "20", "21", "22_to_24"]),
			get_age_percent(["25_to_29", "30_to_34", "35_to_39", "40_to_44"]),
			get_age_percent(["45_to_49", "50_to_54", "55_to_59", "60_to_61", "62_to_64"]),
			get_age_percent(["65_to_66", "67_to_69", "70_to_74", "75_to_79", "80_to_84", "85_plus"]),

			# income
			str(get_float("per_capita_income")),
			str(get_float("median_household_income")),
			get_household_percent([
				"household_below_10", "household_10_to_15", "household_15_to_20", "household_20_to_25", "household_25_to_30",
				"household_30_to_35", "household_35_to_40", "household_40_to_45", "household_45_to_50"
			]),
			get_household_percent(["household_50_to_60", "household_60_to_75", "household_75_to_100"]),
			get_household_percent(["household_100_to_125", "household_125_to_150", "household_150_to_200"]),
			get_household_percent(["household_200_plus"]),
		])
	return processed

def fetch_zcta(zcta, outfile):
	unprocessed = fetch_values(lambda values: c.acs5.zipcode(values, zcta), fields.values())
	rows = process_results(unprocessed, "zip")
	if outfile:
		f = open("data/" + outfile, "w+")
		writer = csv.writer(f)
		writer.writerows(rows)
		f.close()
	else:
		print rows

if __name__ == "__main__":
	fetch_zcta("*", "zips-latest.csv")
	#fetch_zcta("94110", None)
