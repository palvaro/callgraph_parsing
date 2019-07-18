from jaeger_parser import JaegerParser
from graphviz import Digraph




#rules = {
#    'operationName' : "lambda x : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
#    'processID' : 'lambda x : x'
#}


def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)


p = JaegerParser("trace.json")
p.process()

crule = ['serviceName']

# draw the raw graph
rules_raw = {
    'spanID' : 'lambda x : x',
    'operationName' : 'lambda x : x',
    'serviceName' : 'lambda x : x',
}
draw_graph(p.root.transform(rules_raw), "raw", [])



#  project down to serviceName, classic LDFI style
rules1 = {
    'serviceName' : 'lambda x : x if not x.startswith("istio-mixer") else ""',
}
draw_graph(p.root.transform(rules1), "ldfi-raw", crule)

# step 2: collapse adjacent nodes with identical labels
draw_graph(p.root.transform(rules1).collapse(), "ldfi-clean", crule)


# remember timing information as well
rules2 = {
    'serviceName' : 'lambda x : x',
    'startTime' : 'lambda x : x',
    'duration' : 'lambda x : x',
}
draw_graph(p.root.transform(rules2).collapse(), "ldfi2-raw", [])

# but 'forget' timing information during collapse, projecting down to service name.
draw_graph(p.root.transform(rules2).collapse(["serviceName"]), "ldfi2-clean", [])



# finally, create some formulae that we can pass into LDFI
collapsed = p.root.transform(rules2).collapse(crule)
f = collapsed.formula(crule)
print("FORM " + str(f))