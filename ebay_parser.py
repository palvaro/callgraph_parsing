from canonical_tree import CallGraph
from abstract_graphs import DAG, identity, index_of
from graphviz import Digraph
from frozendict import frozendict
import json, sys

def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)

class EbayParser():
    def __init__(self, file):
        fp = open(file, "r")
        self.jsn = json.loads(fp.read())
        fp.close()
    
        self.map = {}
        self.edges = set()
       

    def process(self):
        missing_parents = {}
        data = self.jsn['responseData']

        for item in data:
            labels = {}
            for key in item:
                t = type(item[key])
                if t in (str, int, float):
                    labels[key] = item[key]

            for key in item['dimensions']: 
                #print("%s = %s" % (key, item['dimensions'][key]))
                labels[key] = item['dimensions'][key]

            self.map[item['dimensions']['id']] = labels

        for key in self.map:
            if 'parentId' in self.map[key]:
                print("OK!")
                parent_key = self.map[key]['parentId']
                if parent_key in self.map:
                    parent = self.map[parent_key]
                    pair = (frozendict(parent), frozendict(self.map[key]))
                    self.edges.add(pair)
                else:
                    print("%s is missing parent %s" % (self.map[key], self.map[key]['parentId']))
                    


    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            dag.add_edge(l, r)
        return dag


            

