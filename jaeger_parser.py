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

            labels['serviceName'] = processes[span['processID']]['serviceName']
            for tag in processes[span['processID']]['tags']:
                #print "TAG is " + tag
                labels['process-' + tag['key']] = tag['value']

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


#rules = {
#    'processID' : 'lambda x : x',
#}

#rules = {
#    'operationName' : "lambda x : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
#    'processID' : 'lambda x : x'
#}
            
rules = {
    'serviceName' : 'lambda x : x',
    #'process-ip' : 'lambda x : x',
    'startTime' : 'lambda x : x',
    'duration' : 'lambda x : x',
}


p = JaegerParser("trace2.json")
p.process()


print p.root

nt = p.root.transform(rules)

nt = nt.collapse()

dot = Digraph()
dotfile = nt.todot(dot)
dot.render("foo", view=True)


