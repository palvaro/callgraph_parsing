from zipkin_parser import ZipkinParser, identity
import sys


rules = {
    #'kind': identity,
    'tags_ipv4': identity,
    'tags_serviceName': identity,
    #'tags_request': identity,
    'tags_client': identity,
    #'tags_coordinator': identity
    
}


p = ZipkinParser(sys.argv[1])
p.process()
dag = p.to_abstract()
#dag.transform(rules)
#dag.collapse()


dag.todot("abs")
