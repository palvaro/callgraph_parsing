from jaeger_parser import JaegerParser
from graphviz import Digraph


rules_raw = {
    'serviceName' : 'lambda x : x',
    'spanID' : 'lambda x : x',
}

rules1 = {
    'serviceName' : 'lambda x : x',
}

#rules = {
#    'operationName' : "lambda x : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
#    'processID' : 'lambda x : x'
#}

rules2 = {
    'serviceName' : 'lambda x : x',
    #'process-ip' : 'lambda x : x',
    'startTime' : 'lambda x : x',
    'duration' : 'lambda x : x',
}

def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)


p = JaegerParser("trace.json")
p.process()

crule = ['serviceName']
draw_graph(p.root.transform(rules_raw), "raw", [])



#  project down to serviceName, classic LDFI style
draw_graph(p.root.transform(rules1), "ldfi-raw", crule)

# step 2: collapse adjacent nodes with identical labels
#draw_graph(p.root.transform(rules1).collapse(), "ldfi-clean")


# remember timing information as well
draw_graph(p.root.transform(rules2).collapse(), "ldfi2-raw", crule)

# but 'forget' timing information during collapse, projecting down to service name.
draw_graph(p.root.transform(rules2).collapse(["serviceName"]), "ldfi2-clean", crule)



# finally, create some formulae that we can pass into LDFI
collapsed = p.root.transform(rules2).collapse(crule)
draw_graph(collapsed, "collapsed", crule)
f = collapsed.formula(crule)
print("FORM " + str(f))
