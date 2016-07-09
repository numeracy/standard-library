import census
import csv
import us

def fetch_places():
	c = census.Census("d0aed3790c96f4f43bc7e37bbddae0e55c56ee01")
	places = c.sf1.state_place(("NAME", "P0010001"), "*", "*")

	out_file = open("source-data/sf1-place-pop.csv", "w+")
	writer = csv.writer(out_file)
	writer.writerow(["Place", "State", "Population"])

	for place in places:
		name = place["NAME"].encode("utf-8")
		state = us.states.lookup(place["state"])
		pop = place["P0010001"]
		writer.writerow([name, state, pop])
	out_file.close()

if __name__ == "__main__":
	fetch_places()