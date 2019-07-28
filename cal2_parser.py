from canonical_tree import CallGraph
from graphviz import Digraph
import json

class CalParser():
    def __init__(self, file):
        fp = open(file, "r")
        self.jsn = json.loads(fp.read())
        fp.close()
        self.map = {}
        self.roots = []
       
    def process(self):
        data = self.jsn['responseData']

        for item in data:
            labels = {}
            for key in item:
                t = type(item[key])
                if t in (str, int, float):
                    labels[key] = item[key]
                   
            for key in item['dimensions']: 
                print("%s = %s" % (key, item['dimensions'][key]))
                labels[key] = item['dimensions'][key]

            node = CallGraph(labels)
            self.map[item['dimensions']['id']] = node 
                



        for key in self.map:
            if 'parentId' in self.map[key].labels:
                print("parent is %s" % self.map[key].labels['parentId'])
                parent_key = self.map[key].labels['parentId']#.encode('ascii', 'ignore')


                if parent_key in self.map:
                    parent = self.map[parent_key]
                    parent.add_child(self.map[key])
                else:
                    self.roots.append(self.map[key])
            else:
                print("there is a root")
                self.roots.append(self.map[key])


        return self.roots

