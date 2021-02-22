from graphviz import Digraph
from frozendict import frozendict
import sys

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


class Node:
    def __init__(self, labels={}):
        self.labels = frozendict(labels)
        self.unchanging_hash = hash(self.labels)

    def __eq__(self, other):
        #return self.labels == other.labels
        return self.unchanging_hash == other.unchanging_hash

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

    def __str__(self):
        return str(self.labels) + " (AKA " + str(self.unchanging_hash) + ")"
        
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
            xform = rules

        for item in self.labels:
            #print("item %s, totality %s" % (item, totality))
            if item in xform:
                new_labels[item] = xform[item](self.labels[item], totality.get(item, []), self.labels)
    
            if 'excise' in rules and item in rules['excise']:
                if rules['excise'][item](self.labels[item]):
                    new_labels = {}

        self.labels = frozendict(new_labels)

    


class DAG:
    def __init__(self):
        self.edges = set()
        self.lastrules = {}

    def add_edge(self, left, right):
        self.edges.add((Node(left), Node(right)))


    def collapse(self, rule=[]):
        iters = 0
        while self.collapse_once(rule):
            #dot = self.todot("foo" + str(iters))
            sys.stderr.write(".")
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
        self.lastrules = rules

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

    def __eq__(self, other):
        return self.contains(other) and other.contains(self)
            
    def contains_naive(self, other):
        for l, r in other.edges:
            if (l, r) not in self.edges:
                return False
        return True


    def contains_naive2(self, other):
        # one way to do this interpretation: bag of labels
        obag = map(lambda x: (x[0].label(self.lastrules), x[1].label(self.lastrules)), other.edges)
        lbag = map(lambda x: (x[0].label(self.lastrules), x[1].label(self.lastrules)), self.edges)

        for l, r in obag:
            if (l, r) not in lbag:
                print("Missing from outer: %s ---> %s" % (l, r))
                return False
        return True


    def contains(self, other):
        return self.minus(other) == other.minus(self) == []

    def minus(self, other):
        obag = list(map(lambda x: (x[0].label(self.lastrules), x[1].label(self.lastrules)), other.edges))
        lbag = map(lambda x: (x[0].label(self.lastrules), x[1].label(self.lastrules)), self.edges)
        ret = []
        for l, r in lbag:
            if (l, r) not in obag:
                ret.append((l,r))

        return ret

    def load_db(self):
        ddl = """create table edge (
                    src varchar2[100],
                    dst varchar2[100]
                );
                create table nodelabels (
                    node varchar2[100],
                    label varchar2[100],
                    value varchar2[255]
                );
                create view reachable as
                    with recursive
                        path(x, y) as (
                            select src, dst from edge
                                union all
                            select x, dst from edge e, path p 
                                where e.src = p.y

                        )
                    select * from path;

                create view label_reach as
                    select n1.label as f_lbl, n1.value as f_val, n2.label as t_lbl, n2.value as t_val
                        from reachable p, nodelabels n1, nodelabels n2
                            where p.x = n1.node and p.y = n2.node;
                """ 
        dml = ''
        nodes = set()
        for l,r in self.edges:
            nodes.add(l)
            nodes.add(r)
            dml += "insert into edge values('" + str(l.unchanging_hash) + "', '" + str(r.unchanging_hash) +  "');\n"
        for n in nodes:
            for l in n.labels:
                dml += "insert into nodelabels values ('" + str(n.unchanging_hash) + "', '" + l + "', '" + str(n.labels[l]) + "');\n"


        return ddl + dml
            
        
