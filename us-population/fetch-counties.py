import csv
import requests

def fetch_2000_to_2010():
	for state in csv.DictReader(open("source-data/state-abbreviations.csv")):
		postal_code = state["Postal Code"]
		state_fips = state["FIPS"]

		source_url = "https://www.census.gov/popest/data/intercensal/county/tables/CO-EST00INT-01/CO-EST00INT-01-%s.csv" % state_fips
		resp = requests.get(source_url)

		dest_url = "source-data/counties-2000-2010/%s.csv" % postal_code
		outfile = open(dest_url, "w+")
		outfile.write(resp.content)
		outfile.close()

if __name__ == "__main__":
	fetch_2000_to_2010()