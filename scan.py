import urllib2
import pickle
import string
import os
import glob
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

    with open(AIRPORT_NAMES_FILENAME, 'w+') as f:
        pickle.dump(ports, f)
    return ports


def get_airports_from_pickle():
    f = open(AIRPORT_NAMES_FILENAME, 'r')
    ports = pickle.load(f)
    f.close()
    return ports


def get_airport_data_from_dbpedia(name):
    print name, ':'
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX p: <http://dbpedia.org/property/>
        PREFIX dbowl: <http://dbpedia.org/ontology/>
        PREFIX g: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        SELECT *
        WHERE {
            {
                ?airport a dbowl:Airport;
                p:name ?name
                FILTER regex(?name, '%(name)s', 'i')
            }
            OPTIONAL { ?airport g:geometry ?geo . }
            OPTIONAL{ ?airport p:iata ?iata .  }
            OPTIONAL{ ?airport p:icao ?icao . }
        }
    """ % locals())
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results["results"]["bindings"]

def strip_problem_search_chars(name):
    return name.replace("Int'l.", '').replace("'", '')

def get_airport_data():
    data_path = 'port_data/'
    problem_data_path = 'problem_data/'

    if not os.path.exists(data_path):
        os.makedirs(data_path)
    if not os.path.exists(problem_data_path):
        os.makedirs(problem_data_path)

    for port in  ports:
        fn = port.replace(' ', '').replace('/', '')
        if os.path.exists(data_path + fn) or os.path.exists(problem_data_path + fn):
            print 'data file already exists'
            continue
        port = strip_problem_search_chars(port)
        res = get_airport_data_from_dbpedia(port)
        if len(res) == 1:
            with open(data_path + fn, 'w"') as f:
                pickle.dump(res[0], f)
            print res
        elif len(res) > 1:
            with open(problem_data_path + fn, 'w"') as f:
                pickle.dump(res[0], f)
        elif len(res) == 0:
            with open(problem_data_path + fn + '_notfound', 'w') as f:
                pickle.dump([], f) # just put an empty collection in it

#ports = get_airports_from_skyscanner()
#ports = get_airports_from_pickle()
#get_airport_data()

#fs= glob.glob('problem_data/*_notfound')
#for f in fs:
#    with open(f, 'w') as fw:
#        pickle.dump([], fw)
