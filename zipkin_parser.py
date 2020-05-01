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
    
        print("I have %d spans" % len(self.map.keys()))
        for key in self.map:
            if 'parentId' in self.map[key]:
                print("YES %s" % self.map[key]["id"])
                parent_key = self.map[key]['parentId']
                print("parent key is %s" % parent_key)
                parent = self.map[parent_key]
                #parent.add_child(self.map[key])
                #self.edges.add((frozendict(self.map[key]),  frozendict(labels)))
                pair = (frozendict(parent),  frozendict(self.map[key]))
                print("PAIR IS %s %s" % pair)
                self.edges.add(pair)
            else:
                print("NO parent for %s" % self.map[key])



    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            print("EDg")
            dag.add_edge(l, r)
        return dag
            

p = ZipkinParser("catrace2.json")
p.process()
dag = p.to_abstract()


dag.todot("abs")



