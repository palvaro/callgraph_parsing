from canonical_tree import CallGraph
from abstract_graphs import DAG
from graphviz import Digraph
from frozendict import frozendict
import json

def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)

class XTraceParser():
    def __init__(self, fname):
        fp = open(fname, "r")
        self.jsn = json.load(fp)
        fp.close()
        self.jsn = self.jsn[0]["reports"]
    
        self.map = {}
        self.edges = set()
       
    def process(self):
        for span in self.jsn:
            labels = {}
            for key in span:
                t = type(span[key])
                if t in (str, int, float):
                    labels[key] = span[key]
                elif key != "ParentEventID" and t == list:
                    tmp_label = ""
                    for ind in range(len(span[key])):
                        tmp_label += span[key][ind]
                    labels[key] = tmp_label
            self.map[span['EventID']] = labels
        assert(len(self.map.keys()) == len(self.jsn))

        for span in self.jsn:
            cur_event_id = span["EventID"]
            cur_event = self.map[cur_event_id]
            if "ParentEventID" not in span:
                continue
            for parent_id in span["ParentEventID"]:
                if parent_id in self.map:
                    parent = self.map[parent_id]
                    pair = (frozendict(parent), frozendict(cur_event))
                    self.edges.add(pair)
        assert(len(self.edges) >= (len(self.map.keys()) - 1))

    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            dag.add_edge(l, r)
        return dag

if __name__ == "__main__":
    trace = XTraceParser("hdfs_trace.json")
    trace.process()
    dag = trace.to_abstract()
