from abstract_graphs import DAG, identity, index_of, simple_name
from jaeger_parser import JaegerParser, truncate_cache, truncate_hs
import sys

rules = {
    'operationName': identity,
    'startTime': index_of,
    #'spanID': identity,
    #'processID': identity,
    'serviceName': identity,
    #'process-ip': identity
    'status.code': identity
}

p = JaegerParser(sys.argv[1])
p.process()
dag = p.to_abstract()
dag.transform(rules)
dag.collapse()
#dag.todot('graph1')
print(dag.load_db())