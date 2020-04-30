from graphviz import Digraph
import json, sys
from frozendict import frozendict
from abstract_graphs import DAG, index_of, simple_name, identity

def draw_graph(tree, name):
    dot = Digraph(name)
    dotfile = tree.todot(dot)
    dot.render(name, view=True)

class TFIParser():
    def __init__(self, file):
        fp = open(file, "r")
        self.jsn = json.loads(fp.read())
        fp.close()
        self.requests = {}
        self.nodes = set()
        self.edges = set()

        self.services = {}
       
    def process(self):
        for item in self.jsn['records']:
            if item['uuid'] not in self.requests:
                self.requests[item['uuid']] = []

            if item['service'] not in self.services:
                self.services[item['service']] = []


            payload = item
            self.requests[item['uuid']].append(payload)
            self.services[item['service']].append(payload)

        for r in self.requests:
            services = {}
            svc_all = {}
            for i in self.requests[r]:
                #print("\t%s" % i)

                if i['service'] not in services:
                    services[i['service']] = {}
                    #svc_all[i['service]] = []

                #services[i['service']].append(i)
                #svc_all[i['service']].append(i)


                #services[i['service']][i['type']] = frozenset(i) 
                # because that is how lazy I am
        
                assert(i['type'] not in services[i['service']])
                services[i['service']][i['type']] = frozendict(i)
                #services[i['service']][i['type']] = i


                assert(len(services) < 3)

            if len(services) == 2:
                (l, r) = services.keys()
                #assert(len(services[l][1]) == 1)
                #assert(len(services[r][2]) == 1)
                #print("EDGE: %s ====> %s" % (services[l][1], services[r][2]))
                #print("EDGE2: %s ====> %s" % (services[r][1], services[l][2]))

                self.edges.add((services[l][1], services[r][2]))
                self.edges.add((services[r][1], services[l][2]))

        # in fact, this is how lazy
        for s in self.services:
            frm = None
            for item in sorted(self.services[s], key = lambda foo: foo['timestamp']):    
                if frm is not None:
                    self.edges.add((frozendict(frm), frozendict(item)))
                frm = item

    def node_lbl2(self, node):
        ret = ''
        for k in node:
            ret += k + " : " + str(node[k]) + ", "
    
        return ret

    def node_lbl(self, node):
        return ",".join(map(str, node.values()))

    def short_lbl(self, node):
        return node['service'] + ": " + node.get('message_name', "None") + ": " + str(node['type'])
         
    
    def todot(self, dot):
        #for (l, r, lbl) in self.edges:
        done = set()
        for (l, r) in self.edges:
            if l not in done:
                dot.node(self.node_lbl(l), self.short_lbl(l))
            if r not in done:
                dot.node(self.node_lbl(r), self.short_lbl(r))

            #print("EDGE %s -> %s" % (l, r))
            #dot.edge(l, r, lbl)
            dot.edge(self.node_lbl(l), self.node_lbl(r))
        return dot

    def to_abstract(self):
        dag = DAG()
        for l, r in self.edges:
            dag.add_edge(l, r)

        return dag




