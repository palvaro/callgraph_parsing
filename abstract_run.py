from zipkin_parser import ZipkinParser
from jaeger_parser import JaegerParser
from tfi_parser import TFIParser
from ebay_parser import EbayParser
from xtrace_parser import XTraceParser
from abstract_graphs import identity, index_of, simple_name
import sys


cls = ZipkinParser
l = len(sys.argv)

if l < 2 or l > 3:
    print("sorry, one or two arguments")
    sys.exit(1)
elif l == 3:
    if sys.argv[2] in ["JaegerParser", "ZipkinParser", "TFIParser", "EbayParser", "XTraceParser"]:    
        cls = eval(sys.argv[2])
    else:
        print("using default %s, don't recognize %s" % (cls, sys.argv[2]))


rules2 = {
    #'kind': identity
    #'service': simple_name,
    #'timestamp': index_of
    #'message_name': identity
    #'poolname': identity
    'operationName': identity,
    'processID': identity,
    'component': identity,
    'peer.address': identity,
    'http.url': identity,
    'http.host': identity,
    'serviceName': identity,
}

rules = {
    #'ThreadID': index_of,
    'Source': lambda x,y,z: x.split(':')[0],
    #'Agent': identity,
    #'ProcessID': index_of
}


p = cls(sys.argv[1])
p.process()
dag = p.to_abstract()
dag.transform(rules)
dag.collapse()
#

dag.todot("abs")

print(dag.load_db())

