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

        processes = {}
        for process in data[0]['processes']:
            processes[process] = data[0]['processes'][process]

        for span in data[0]['spans']:
            labels = {}
            for key in span:
                t = type(span[key])
                if t in (str, int, float):
                    #print("yay %s" % key)
                    labels[key] = span[key]
                #else:
                #    print("nay %s - %s" % (key, t))
            for tag in span['tags']:
                labels[tag['key']] = tag['value']

            if 'references' in span:
                for item in span['references']:
                    if item['refType'] == "CHILD_OF":
                        labels["parent_span"] = item['spanID']

            labels['serviceName'] = processes[span['processID']]['serviceName']
            for tag in processes[span['processID']]['tags']:
                labels['process-' + tag['key']] = tag['value']

            node = CallGraph(labels)
            self.map[span['spanID']] = node

        for key in self.map:
            if 'parent_span' in self.map[key].labels:
                parent_key = self.map[key].labels['parent_span']#.encode('ascii', 'ignore')
                parent = self.map[parent_key]
                parent.add_child(self.map[key])
            else:
                self.root = self.map[key]


        return self.root
