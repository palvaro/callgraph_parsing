from cal_parser import CalTrace
from graphviz import Digraph




#rules = {
#    'operationName' : "lambda x : '' if x.startswith('async') or x.startswith('/istio') or x.startswith('kubernetes') else x",
#    'processID' : 'lambda x : x'
#}


def draw_graph(tree, name, rule):
    dot = Digraph(name)
    dotfile = tree.todot(dot, rule)
    dot.render(name, view=True)


p = CalTrace("viewitem.json")
p.process()

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
for root in p.roots:
    draw_graph(root.transform(rules_raw), "raw", [])



#  project down to serviceName, classic LDFI style
rules1 = {
    'transform' : {
        'pool' : 'lambda x : x',
    },
    'excise': {
        'pool' : 'lambda x : re.search("elasticsearch", x, re.IGNORECASE)'
    }
}
for root in p.roots:
    draw_graph(root.transform(rules1), "ldfi-raw", crule)

# step 2: collapse adjacent nodes with identical labels
for root in p.roots:
    draw_graph(root.transform(rules1).collapse(), "ldfi-clean", crule)

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
for root in p.roots:
    draw_graph(root.transform(rules2).collapse(), "ldfi2-raw", [])

# but 'forget' timing information during collapse, projecting down to service name.
for root in p.roots:
    draw_graph(root.transform(rules2).collapse(["pool"]), "ldfi2-clean", [])



# finally, create some formulae that we can pass into LDFI
for root in p.roots:
    collapsed = root.transform(rules2).collapse(crule)
    f = collapsed.formula(crule)
    print("FORM " + str(f))
