from canonical_tree import CallGraph
from graphviz import Digraph
import json

root = CallGraph({})


a = CallGraph({'id': '1', 'op': 'open', 'time': '1234'})
b = CallGraph({'id': '2', 'op': 'read', 'time': '1237'})
c = CallGraph({'id': '3', 'op': 'write', 'time': '1267'})
a.add_child(b)
b.add_child(c)


d = CallGraph({'id': '4', 'op': 'read', 'time': '1334'})
e = CallGraph({'id': '5', 'op': 'read', 'time': '1367'})
f = CallGraph({'id': '6', 'op': 'write', 'time': '1368'})
g = CallGraph({'id': '7', 'op': 'read', 'time': '1600'})

b.add_child(e)

d.add_child(e)
e.add_child(f)
f.add_child(g)

root.add_child(a)
root.add_child(d)



dot = Digraph()
dot2 = Digraph()
dot3 = Digraph(strict=True)


rules = {
    'op': lambda x,y,z: x,
    #'id': lambda x,y,z: x,
    #'time': lambda x,y,z: x
}

print("OK OK") 

root.todot(dot)

root.transform(rules)


root.todot(dot2)


root.collapse()
root.collapse()

root.todot(dot3)

dot.render("test")
dot2.render("test2")
dot3.render("test3")



