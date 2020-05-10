from zipkin_parser import ZipkinParser
from jaeger_parser import JaegerParser
from tfi_parser import TFIParser
from abstract_graphs import identity, index_of, simple_name
import sys


cls = ZipkinParser
l = len(sys.argv)

print("l is %d" % l)
if l < 3 or l > 4:
    print("This is a diff program and requires at least two arguments")
    sys.exit(1)
elif l == 4:
    if sys.argv[3] in ["JaegerParser", "ZipkinParser", "TFIParser"]:    
        cls = eval(sys.argv[3])


rules = {
    #'kind': identity
    #'service': simple_name,
    #'timestamp': index_of
    #'message_name': identity
}


p = cls(sys.argv[1])
p.process()
dag = p.to_abstract()
dag.transform(rules)
dag.collapse()


dag.todot("abs")


p2 = cls(sys.argv[2])
p2.process()



dag2 = p2.to_abstract()
dag2.transform(rules)
dag2.collapse()

#print(dag == dag2)

if (dag == dag2):
    print("Samesies")
else:
    for (l,r) in dag.minus(dag2):
        print("<<<< %s -> %s" % (l, r))
    for (l,r) in dag2.minus(dag):
        print(">>>> %s -> %s" % (l, r))    




dag2.todot("abs2")
