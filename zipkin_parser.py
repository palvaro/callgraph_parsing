from canonical_tree import CallGraph
from abstract_graphs import DAG
from graphviz import Digraph
from frozendict import frozendict
import json

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
            print("SPAN %s" % span)            
            labels = {}
            for key in span:
                t = type(span[key])
                if t in (str, int, float):
                    labels[key] = span[key]

            
            self.map[span['id']] = labels

        for key in self.map:
            if 'parentId' in self.map[key]:
                parent_key = self.map[key]['parentId']#.encode('ascii', 'ignore')
                parent = self.map[parent_key]
                #parent.add_child(self.map[key])
                self.edges.add((frozendict(self.map[key]),  frozendict(labels)))



    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            dag.add_edge(l, r)
        return dag
            

p = ZipkinParser("catrace0.json")
p.process()
dag = p.to_abstract()


dag.todot("abs")



