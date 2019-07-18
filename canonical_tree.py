class CallGraph():
    def __init__(self, labels={}):
        self.labels = labels
        self.children = set()

    def add_child(self, child):
        self.children.add(child)

    def name(self):
        #return str(self.labels)
        return self.label()

    def label(self):
        #return self.labels.values()[0]
        #return str(self.labels)
        st = ''
        for k in self.labels:
            st += k + '=' + str(self.labels[k]) + ","

        return st


    def __str__(self):
        return str(self.labels) + '(' + ','.join(map(lambda x: str(x), self.children))  + ')'

    def todot(self, dot):
        dot.node(self.name(), self.label())
        for c in self.children:
            print "c is " + str(c)
            c.todot(dot)
            dot.edge(self.name(), c.name())

    def transform(self, rules):
        new_labels = {}
        for item in self.labels:
            if item in rules:
                # forgive me for this!
                exec("lmb = " + rules[item])
                new_labels[item] = lmb(self.labels[item])
        new_node = CallGraph(new_labels)
        for c in self.children:
            new_node.add_child(c.transform(rules))

        return new_node

    def equiv(self, other, rule):
        if isinstance(other, self.__class__):
            #return self.labels == other.labels
            if rule == []:
                return self.labels == other.labels
            else:
                for lbl in rule:
                    if self.labels[lbl] != other.labels[lbl]:
                        return False
                return True
        else:
            return False

    def collapse(self, rule=[]):
        # this one is gonna be tricky
        new_node = CallGraph(self.labels)

        working = []
        for child in self.children:
            working.append(child)

        for child in working:
            if child.equiv(self, rule):
                print "samesies"
                for c in child.children:
                    print "OOO"
                    working.append(c)
            else:
                new_node.add_child(child.collapse(rule)) 

        return new_node
        




