from tfi_parser import TFIParser
from abstract_graphs import index_of, simple_name, identity
import sys

rules = {
    'transform': {
        #'uuid': simple_name,
        #'service': simple_name,
        #'uuid': identity,
        'service': identity,
        'message_name': identity,
        #'service': identity
        'timestamp': index_of
        #'timestamp': identity
        #'type': lambda x,y,z: x
        #'message_name': lambda x,y,z: x if z['type'] == 1 else False
    },

    'excise': {
        'type': lambda x: x == 2
    }


}



p = TFIParser(sys.argv[1])
p.process()

names = sys.argv[1].split('.')
names.pop()
names.append("graph")
names = ".".join(names)


cg = p.to_abstract()
cg.transform(rules)

#cg.todot(names+ "_cg1")

print("EDGES %d" % len(cg.edges))
print("COLLAPSES %d" % cg.collapse())

print("EDGES %d" % len(cg.edges))




#draw_graph(p, names)
cg.todot(names+ "_cg2")


