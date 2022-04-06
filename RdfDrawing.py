from rdflib import Literal
from rdflib.namespace import RDFS
import rdflib
from rdflib.plugins.sparql import prepareQuery
import RDFNode as rdfnode
import Utils as Utils
import DrawIOUtils as DrawIOUtils
import logging

'''
This class contains methods to create draw.io schema
'''
class RdfDrawing:
    GRAPH = None
    HEADERS = "id,name,fill,stroke,shape"
    SHAPE_OUTLINE_COLOR = "#000000"
    INSTANCE_COLOR = "#FFE6CC"
    INSTANCE_SHAPE = "rhombus"
    CLASS_COLOR = "#d5e8d4"
    CLASS_SHAPE = "rounded"
    LITERAL_COLOR = "#DAE8FC"
    LITERAL_SHAPE = "ellipse"
    SKIP_RDF_LABEL = True
    UTILS = Utils.Utils()
    DRAW_IO_UTILS = DrawIOUtils.DrawIOUtils()

    def get_draw_io_csv(self, input_file):
        '''
        Create draw.io csv.
        :param input_file: RDF file
        :return: draw.io csv text.
        '''
        self.LABELS = {}
        self.LABELS_USED = {}
        self.GRAPH = rdflib.Graph()
        self.GRAPH.parse(input_file, format="text/turtle")

        predicates_location = {}

        template = open('template/draw-io-template', 'r').read()

        # Query to list all predicates
        query = open('queries/list_predicates.rq', 'r').read()
        q = prepareQuery(query)

        counter = 0

        for row in self.GRAPH.query(q):
            url = row[0]
            if url == RDFS.label and self.SKIP_RDF_LABEL:
                logging.info("skiping rdfs:label")
            else:
                predicate_label = self.__get_labels(url, True)
                connect_text = self.DRAW_IO_UTILS.get_connection_text(predicate_label)
                template = template + "\n" + connect_text
                predicates_location[url] = counter
                counter = counter + 1

        header = self.HEADERS

        for key in predicates_location:
            code = self.__get_labels(key, True)
            code = self.UTILS.clean_label(code)
            header = header + "," + code

        template = template + "\n" + header

        # Query to list all triples
        query = open('queries/list_triples.rq', 'r').read()
        q = prepareQuery(query)
        nodes = {}

        for row in self.GRAPH.query(q):
            sub = row[0]
            pre = row[1]
            obj = row[2]
            if sub not in nodes:
                sub_label = self.__get_labels(sub, True)
                if self.UTILS.is_uri_instance(self.GRAPH, sub):
                    sub_type = RDFS.Resource
                    sub_shape = self.INSTANCE_SHAPE
                    sub_color = self.INSTANCE_COLOR
                else:
                    sub_type = RDFS.Class
                    sub_shape = self.CLASS_SHAPE
                    sub_color = self.CLASS_COLOR

                connections = self.__get_connection_template__(predicates_location)

                for subj, prede in self.GRAPH.subject_predicates(sub):
                    if prede in predicates_location:
                        indx = predicates_location[prede]
                        connect_label = subj

                        if connections[indx] == "NA":
                            connections[indx] = connect_label
                        else:
                            connections[indx] = connections[indx] + "," + connect_label

                rnd = rdfnode.RDFNode(sub, sub_label, sub_type, connections, sub_color, self.SHAPE_OUTLINE_COLOR,
                                                                                       sub_shape)
                nodes[sub] = rnd

            if pre == RDFS.label and self.SKIP_RDF_LABEL:
                logging.info("skiping rdfs:label")
            elif obj not in nodes:
                if not isinstance(obj, Literal):
                    obj_label = self.__get_labels(obj, True)

                    if self.UTILS.is_uri_instance(self.GRAPH, obj):
                        obj_type = RDFS.Resource
                        obj_shape = self.INSTANCE_SHAPE
                        obj_color = self.INSTANCE_COLOR
                    else:
                        obj_type = RDFS.Class
                        obj_shape = self.CLASS_SHAPE
                        obj_color = self.CLASS_COLOR
                else:
                    obj_label = obj
                    obj_type = RDFS.Literal
                    obj_shape = self.LITERAL_SHAPE
                    obj_color = self.LITERAL_COLOR

                    if obj_label not in self.LABELS_USED:
                        self.LABELS_USED[obj_label] = 1
                    else:
                        self.LABELS_USED[obj_label] = self.LABELS_USED[obj_label] + 0
                        obj_label = str(obj_label) + " [Duplicate " + str(self.LABELS_USED[obj_label]) + "]"

                connections = self.__get_connection_template__(predicates_location)

                for subj, prede in self.GRAPH.subject_predicates(obj):
                    if prede in predicates_location:
                        indx = predicates_location[prede]
                        connect_label =  subj

                        if connections[indx] == "NA":
                            connections[indx] = connect_label
                        else:
                            connections[indx] = connections[indx] + "," + connect_label

                rnd = rdfnode.RDFNode(obj, obj_label, obj_type, connections, obj_color, self.SHAPE_OUTLINE_COLOR,
                                      obj_shape)
                nodes[obj] = rnd

        logging.info("Num of nodes " + str(len(nodes)))

        for key in nodes:
            node = nodes[key]
            node_text = node.ID + "," + node.NAME + "," + node.NODE_COLOR + "," + node.NODE_OUTLINE_COLOR
            node_text = node_text + "," + node.NODE_SHAPE
            connects_text = ""

            for connect in node.CONNECTION:
                connects_text = connects_text + '"' + connect + '"' + ","

            connects_text = connects_text[:-1]
            node_text = node_text + "," + connects_text
            template = template + "\n" + node_text
        return template

    def __get_connection_template__(self, predicates_location):
        '''
        This method creates default connection text
        :param predicates_location: list of predicates
        :return: Default connection text
        '''

        template = []
        for key in predicates_location:
            template.append("NA")
        return template

    def __get_labels(self, url, use_ontobee):
        '''
        Get label of a url
        :param url: url
        :param use_ontobee: True or False (If ontobee should be used)
        :return: Label
        '''
        label = None

        if url in self.LABELS:
            return self.LABELS[url]

        # Query to get labels from graph
        query = open('queries/get_label_from_graph.rq', 'r').read()
        q = prepareQuery(query)

        # Add labels to instances
        for row in self.GRAPH.query(q, initBindings={'uri': url}):
            if row[1]:
                label = row[1]

        if use_ontobee and not label:
            label = self.UTILS.get_label_from_ontobee(url)

        if not label:
            label = self.UTILS.get_suffix(url)

        # to handle duplicate labels
        if label not in self.LABELS_USED:
            self.LABELS_USED[label] = 0
        else:
            self.LABELS_USED[label] = self.LABELS_USED[label] + 1
            label = str(label) + " [Duplicate " + str(self.LABELS_USED[label]) + "]"

        # Skip prefix for instances
        if not self.UTILS.is_uri_instance(self.GRAPH, url):
            prefix = self.UTILS.get_prefix(url, self.UTILS.get_suffix(url))
            label = prefix + ":" + label

        self.LABELS[url] = label
        return label