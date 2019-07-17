from canonical_tree import CallGraph
from graphviz import Digraph
import json

class JaegerParser():
    def __init__(self, file):
        fp = open(file, "r")
        self.jsn = json.loads(fp.read())
        fp.close()
    
        self.map = {}


    def process(self):
        data = self.jsn['data']
        assert(len(data) == 1)
        for span in data[0]['spans']:
            #print span
            labels = {}
            for key in span:
                #print "key " + key
                t = type(span[key])
                if t in (str, int, float, unicode):
                    labels[key] = span[key]
            for tag in span['tags']:
                labels[tag['key']] = tag['value']

            if 'references' in span:
                for item in span['references']:
                    if item['refType'] == "CHILD_OF":
                        labels["parent_span"] = item['spanID']

            node = CallGraph(labels)
            self.map[span['spanID']] = node

        for key in self.map:
            print "key *" + key + "*"
            if 'parent_span' in self.map[key].labels:
                parent_key = self.map[key].labels['parent_span'].encode('ascii', 'ignore')
                print "parent key is *" + parent_key + "*"
                parent = self.map[parent_key]
                parent.add_child(self.map[key])
            else:
                self.root = self.map[key]
            


p = JaegerParser("trace.json")
p.process()


print p.root

dot = Digraph()
dotfile = p.root.todot(dot)
dot.render("foo", view=True)
