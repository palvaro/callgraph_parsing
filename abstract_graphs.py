from graphviz import Digraph
from frozendict import frozendict

sorts = {}
def index_of_memo(x, y, z):
    if id(y) not in sorts:
        sorts[id(y)] = {}
        for idx, val in enumerate(sorted(map(lambda q: int(q), y))):
            # N.B. again, assuming unique and picking a different winner!
            sorts[id(y)][val] = idx
    return sorts[id(y)][int(x)]

def index_of(x, y, z):
    # decidedly not fast!  pls optimize
    for idx, val in enumerate(sorted(map(lambda q: int(q), y))):
        # assumes values to be unique!! ono
        if val == int(x):
            return idx

def simple_name(x, y, z):
    for idx, val in enumerate(sorted(y)):
        if val == x:
            return chr(ord('@') + idx + 1)

def identity(x, y, z):
    return x


class Node():
    def __init__(self, labels={}):
        self.labels = frozendict(labels)
        self.unchanging_hash = hash(self.labels)

    def __eq__(self, other):
        #return self.labels == other.labels
        return self.unchanging_hash == self.unchanging_hash

    def equiv(self, other, rule):
        if isinstance(other, self.__class__):
            #return self.labels == other.labels
            if rule == []:
                return self.labels == other.labels
            else:
                for lbl in rule:
                    if lbl not in self.labels:
                        return False
                    if lbl not in other.labels:
                        return False
                    if self.labels[lbl] != other.labels[lbl]:
                        return False
                return True
        else:
            return False

    

    def __hash__(self):
        #return hash(self.labels)
        return self.unchanging_hash
        
    def label(self, rule):
        st = ''
        for k in self.labels:
            if k in rule or rule == []:
                st += k + '=' + str(self.labels[k]) + ","
        return st

    def ident(self):
        return str(abs(self.__hash__()))

    def transform(self, rules, totality={}):
        new_labels = {}
        if 'transform' in rules and 'excise' in rules:
            xform = rules['transform']
        else:
            # for backwards compatibility while I play
            print("bw")
            xform = rules

        for item in self.labels:
            #print("item %s, totality %s" % (item, totality))
            if item in xform:
                new_labels[item] = xform[item](self.labels[item], totality.get(item, []), self.labels)
    
            if 'excise' in rules and item in rules['excise']:
                if rules['excise'][item](self.labels[item]):
                    new_labels = {}

        self.labels = frozendict(new_labels)

    


class DAG():
    def __init__(self, edges = set()):
        self.edges = edges

    def add_edge(self, left, right):
        self.edges.add((Node(left), Node(right)))


    def collapse(self, rule=[]):
        iters = 0
        while self.collapse_once(rule):
            #dot = self.todot("foo" + str(iters))
            print(".")
            iters += 1
            #if iters > 10:
            #    return iters

        return iters

    def collapse2(self, rule=[]):
        return self.collapse_once(rule)

    def collapse_once(self, rule):
        successor = {}
        predecessor = {}
        for l, r in self.edges:
            if l not in successor:
                successor[l] = set()
            successor[l].add(r)

            if r not in predecessor:
                predecessor[r] = set()
            predecessor[r].add(l)

        # just make one pass. batch up the deletions. reinvoke till fixed point
        deletions = set()
        additions = set()
        for l, r in self.edges.copy():
            if r.label(rule) == "" or r.equiv(l, rule):
                #deletions.add((l, r))
                if r in successor:
                    for s in successor[r]:
                        #if l != s:
                        additions.add((l, s))
                        deletions.add((r, s))

                if r in predecessor:
                    for p in predecessor[r]:
                        if p != l:
                            additions.add((p, l))
                        deletions.add((p, r))

                for d in deletions:
                    self.edges.remove(d)
                for a in additions:
                    self.edges.add(a)
                return True
            
        #for d in deletions:
        #    self.edges.remove(d)
        #for a in additions:
        #    self.edges.add(a)

        #return len(deletions)


    def transform(self, rules):
        # first, gather up our totality
        # TODO
        totality = {}
        for l, r in self.edges:
            for x in [l, r]:
                for label in x.labels:
                    if label not in totality:
                        totality[label] = set()
                    totality[label].add(x.labels[label])

        # then do the rest
        for l, r in self.edges:
            # should be idempotent so let's not worry too much for now
            l.transform(rules, totality)
            r.transform(rules, totality)

    def todot(self, name):
        dot = Digraph()
        nodes = set()
        for l,r in self.edges:
            if l not in nodes:
                dot.node(l.ident(), l.label([]))
                nodes.add(l)
            if r not in nodes:
                dot.node(r.ident(), r.label([]))
                nodes.add(r)

            dot.edge(l.ident(), r.ident())

        dot.render(name, view=True)
            
        