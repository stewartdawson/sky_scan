import urllib2
import pickle
import string
from BeautifulSoup import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON

AIRPORT_NAMES_FILENAME = 'airports.list'

def get_airports_from_skyscanner():
	ports = []
	for letter in string.ascii_lowercase:
		url = 'http://www.skyscanner.net/flights-to/airports-of-the-world.html?letter=' + letter
		page = urllib2.urlopen(url).read()
		soup = BeautifulSoup(page)
		airports = soup.findAll('table', 'sm_table sm_table_sections2')[1].findAll('a')
		ports.extend([a.text[:-7] for a in airports])

	f = open(AIRPORT_NAMES_FILENAME, 'w+')
	pickle.dump(ports, f)
	f.close()
	return ports


def get_airports_from_pickle():
	f = open(AIRPORT_NAMES_FILENAME, 'r')
	ports = pickle.load(f)
	f.close()
	return ports


#ports = get_airports_from_skyscanner()
#ports = get_airports_from_pickle()

#print ports
#print len(ports), 'airports found'


sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX p: <http://dbpedia.org/property/>
    PREFIX dbowl: <http://dbpedia.org/ontology/>
    PREFIX g: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    SELECT *
    WHERE {
    ?airport a dbowl:Airport;
    p:name ?name;
    g:geometry ?geo;
    p:iata ?iata;
    p:icao ?icao.
    FILTER regex(?name, 'Glasgow International', 'i')
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
	print result
