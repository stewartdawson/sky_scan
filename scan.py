import urllib2
import pickle
import string
from BeautifulSoup import BeautifulSoup


def get_airports_from_skyscanner():  	
	ports = []
	for letter in string.ascii_lowercase:
		url = 'http://www.skyscanner.net/flights-to/airports-of-the-world.html?letter=' + letter
		page = urllib2.urlopen(url).read()
		soup = BeautifulSoup(page)
		airports = soup.findAll('table', 'sm_table sm_table_sections2')[1].findAll('a')
		for airport in airports:
			ports.append(airport.text[:-7])
	
	f = open('airports.list', 'w+')
	pickle.dump(ports, f)
	f.close()

	return ports


def get_airports_from_pickle():
	f = open('airports.list', 'r')
	ports = pickle.load(f)
	f.close()
	return ports


#ports = get_airports_from_skyscanner()
ports = get_airports_from_pickle()

print ports
print len(ports), 'airports found'
