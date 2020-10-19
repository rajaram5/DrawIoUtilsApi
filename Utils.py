from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib.plugins.sparql import prepareQuery
import requests
import json
import hashlib
from string import digits

'''
This class contains some utils methods
'''
class Utils:

    ONTOBEE_ENDPOINT = "http://sparql.hegroup.org/sparql"
    PREFIX_CC_ENPOINT = "http://prefix.cc/reverse"
    PREFIXS = {}

    def get_label_from_ontobee(self, uri):
        '''
        Query ontobee to get label of uri
        :param uri: uri
        :return: Label of uri
        '''

        sparql = SPARQLWrapper(self.ONTOBEE_ENDPOINT)
        # Get label query
        query = open('queries/get_label.rq', 'r').read()
        query = query.replace("URI", uri)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results["results"]["bindings"]:
            if result["label"]["value"]:
                label = str(result["label"]["value"])
                if label:
                    return label

    def is_uri_instance(self, graph, url):
        '''
        Check if url is of type instance
        :param graph: RDF graph
        :param url: url
        :return: True or False (If url is an instance)
        '''

        # Query to get instance type
        query = open('queries/get_type_of_instance.rq', 'r').read()
        q = prepareQuery(query)

        for row in graph.query(q, initBindings={'ins': url}):
            if row[0]:
                return True
            else:
                return False


    def clean_label(self, label):
        '''
        Clean text by removing spce and special chars
        :param label: String object
        :return: Cleaned rexr
        '''

        label = label.replace(" ", "")
        label = label.replace("-", "_")
        label = label.replace(":", "_")
        return label


    def get_suffix(self, url):
        '''
        Get suffix of a url
        :param url: url
        :return: sufix of a url
        '''
        sufffix = url.split("/")[-1]

        if not sufffix:
            sufffix = url.split("#")[-1]
        if '#' in sufffix:
            sufffix = sufffix.split("#")[-1]

        return sufffix

    def get_prefix(self, url, suffix):
        '''
        Get prefix of a url
        :param url: url
        :param suffix: suffix of url
        :return: prefix of a url
        '''
        prefix_url = url[:-len(suffix)]

        if prefix_url not in self.PREFIXS:
            payload = {'uri': prefix_url, 'format': 'json'}
            r = requests.get(self.PREFIX_CC_ENPOINT, params=payload)

            if r.status_code == requests.codes.ok:
                data = json.loads(r.text)
                for key, value in data.items():
                    return key
            else:
                hash = hashlib.sha1(prefix_url.encode("UTF-8")).hexdigest()
                remove_digits = str.maketrans('', '', digits)
                hash_without_numbers = hash.translate(remove_digits)
                value = hash_without_numbers[:6]
                return value
        else:
            return self.PREFIXS[prefix_url]