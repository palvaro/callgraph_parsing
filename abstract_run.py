from zipkin_parser import ZipkinParser
from jaeger_parser import JaegerParser
from tfi_parser import TFIParser
from ebay_parser import EbayParser
from abstract_graphs import identity, index_of, simple_name
import sys


cls = ZipkinParser
l = len(sys.argv)

print("l is %d" % l)
if l < 2 or l > 3:
    print("This is a diff program and requires at least two arguments")
    sys.exit(1)
elif l == 3:
    if sys.argv[2] in ["JaegerParser", "ZipkinParser", "TFIParser", "EbayParser"]:    
        cls = eval(sys.argv[2])


rules = {
    #'kind': identity
    #'service': simple_name,
    #'timestamp': index_of
    #'message_name': identity
    'poolname': identity
}


p = cls(sys.argv[1])
p.process()
dag = p.to_abstract()
dag.transform(rules)
dag.collapse()


dag.todot("abs")

