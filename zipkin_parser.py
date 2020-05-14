from canonical_tree import CallGraph
from abstract_graphs import DAG, identity
from graphviz import Digraph
from frozendict import frozendict
import json, sys

def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)

class ZipkinParser():
    def __init__(self, file):
        fp = open(file, "r")
        self.jsn = json.loads(fp.read())
        fp.close()
    
        self.map = {}
        self.edges = set()
       
    def process(self):
        for span in self.jsn:
            labels = {}
            for key in span:
                t = type(span[key])
                if t in (str, int, float):
                    labels[key] = span[key]
                elif t == dict:
                    for k in span[key]:
                        nk = key + "_" + k
                        labels[nk] = span[key][k]
            self.map[span['id']] = labels
    
        for key in self.map:
            if 'parentId' in self.map[key]:
                parent_key = self.map[key]['parentId']
                parent = self.map[parent_key]
                pair = (frozendict(parent),  frozendict(self.map[key]))
                self.edges.add(pair)
                    


    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            dag.add_edge(l, r)
        return dag


            

