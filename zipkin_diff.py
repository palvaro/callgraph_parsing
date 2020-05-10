from zipkin_parser import ZipkinParser, identity
import sys


rules = {
    'kind': identity
}


p = ZipkinParser(sys.argv[1])
p.process()
dag = p.to_abstract()
dag.transform(rules)
dag.collapse()


dag.todot("abs")


p2 = ZipkinParser(sys.argv[2])
p2.process()



dag2 = p2.to_abstract()
dag2.transform(rules)
dag2.collapse()

print(dag == dag2)



dag2.todot("abs2")
