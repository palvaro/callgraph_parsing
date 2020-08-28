from canonical_tree import CallGraph
from abstract_graphs import Node, DAG, identity, index_of, simple_name
from graphviz import Digraph
import json
from frozendict import frozendict

p = DAG()

o = {'id': 'A', 'op': 'open', 'time': '0'}
a = {'id': 'A', 'op': 'open', 'time': '1'}
b = {'id': 'B', 'op': 'read', 'time': '2'}
c = {'id': 'B', 'op': 'read', 'time': '3'}
c1 = {'id': 'B', 'op': 'write', 'time': '4'}
d = {'id': 'C', 'op': 'read', 'time': '3'}
e = {'id': 'C', 'op': 'read', 'time': '5'}
f = {'id': 'C', 'op': 'write', 'time': '6'}
g = {'id': 'D', 'op': 'read', 'time': '7'}
h = {'id': 'D', 'op': 'read', 'time': '8'}

p.add_edge(o, a)
p.add_edge(a, b)
p.add_edge(b, c)
p.add_edge(c, c1)
p.add_edge(d, c)
p.add_edge(o, d)
p.add_edge(b, e)
p.add_edge(d, e)
p.add_edge(e, f)
p.add_edge(f, g)
p.add_edge(f, h)


rules = {
    'op': identity,
    'id': identity,
    #'time': identity,
}

p.transform(rules)
p.collapse()
p.todot("testy test")



