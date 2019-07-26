from cal_parser import CalTrace
from graphviz import Digraph




#rules = {
#    'operationName' : "lambda x : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
#    'processID' : 'lambda x : x'
#}


def draw_graph(trees, name, rule):
    dot = Digraph(name)
    for tree in trees:
        tree.todot(dot, rule)
    dot.render(name, view=True)


p = CalTrace("viewitem.json")

crule = ['pool']

# draw the raw graph
rules_raw = {
    'transform' : {
        'id' : 'lambda x : x',
        'pool' : 'lambda x : x',
    },
    'excise': {
        'pool' : 'lambda x : re.search("elasticsearch", x, re.IGNORECASE)'
    }
}
new_roots = []
for root in p.roots:
    new_roots.append(root.transform(rules_raw))
draw_graph(new_roots, "raw", [])


#  project down to serviceName, classic LDFI style
rules1 = {
    'transform' : {
        'pool' : 'lambda x : x',
    },
    'excise': {
        'pool' : 'lambda x : re.search("elasticsearch", x, re.IGNORECASE)'
    }
}
new_roots = []
for root in p.roots:
    new_roots.append(root.transform(rules1))
draw_graph(new_roots, "ldfi-raw", crule)

# step 2: collapse adjacent nodes with identical labels
new_roots = []
for root in p.roots:
    new_roots.append(root.transform(rules1).collapse())
draw_graph(new_roots, "ldfi-clean", crule)

# remember timing information as well
rules2 = {
    'transform' : {
        'pool' : 'lambda x : x',
        'startTime' : 'lambda x : x',
        'duration' : 'lambda x : x',
    },
    'excise': {
        'pool' : 'lambda x : re.search("elasticsearch", x, re.IGNORECASE)'
    }
}
new_roots = []
for root in p.roots:
    new_roots.append(root.transform(rules2).collapse())
draw_graph(new_roots, "ldfi2-raw", [])

# but 'forget' timing information during collapse, projecting down to service name.
new_roots = []
for root in p.roots:
    new_roots.append(root.transform(rules2).collapse(["pool"]))
draw_graph(new_roots, "ldfi2-clean", [])



# finally, create some formulae that we can pass into LDFI
for root in p.roots:
    collapsed = root.transform(rules2).collapse(crule)
    f = collapsed.formula(crule)
    print("FORM " + str(f))
