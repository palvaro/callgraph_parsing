from jaeger_parser import JaegerParser
from graphviz import Digraph
import sys
from canonical_tree import index_of




rules_pid = {
    #'operationName' : "lambda x, y : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
    'processID' : lambda x, y : x,
    'startTime' : index_of
}


def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)


p = JaegerParser("trace.json")
p.process()

crule = ['serviceName']

# draw the raw graph
rules_raw = {
    'transform' : {
        'spanID' : lambda x, y : x,
        'operationName' : lambda x, y : x,
        'serviceName' : lambda x, y : x,
    },
    'excise': {
        'serviceName' : lambda x : x.startswith("istio-mixer")
    }
}

lbls = p.root.label_values()

draw_graph(p.root.transform(rules_pid, lbls).collapse(), "raw", [])
sys.exit(1)



#  project down to serviceName, classic LDFI style
rules1 = {
    'transform' : {
        'serviceName' : lambda x, y : x if not x.startswith("istio-mixer") else "",
    },
    'excise': {
        'serviceName' : lambda x: x.startswith("istio-mixer")
    }
}
draw_graph(p.root.transform(rules1), "ldfi-raw", crule)

# step 2: collapse adjacent nodes with identical labels
draw_graph(p.root.transform(rules1).collapse(), "ldfi-clean", crule)


# remember timing information as well
rules2 = {
    'transform' : {
        'serviceName' : lambda x, y : x,
        'startTime' : lambda x, y : x,
        'duration' : lambda x, y : x,
    },
    'excise': {
        'serviceName' : lambda x : x.startswith("istio-mixer")
    }
}
draw_graph(p.root.transform(rules2).collapse(), "ldfi2-raw", [])

# but 'forget' timing information during collapse, projecting down to service name.
draw_graph(p.root.transform(rules2).collapse(["serviceName"]), "ldfi2-clean", [])



# finally, create some formulae that we can pass into LDFI
collapsed = p.root.transform(rules2).collapse(crule)
f = collapsed.formula(crule)
print("FORM " + str(f))


lbls = p.root.label_values()
for k in lbls:
    print(k)
    for v in lbls[k]:
        print("\t %s" % v)
