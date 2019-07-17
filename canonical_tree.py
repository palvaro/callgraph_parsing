class CallGraph():
    def __init__(self, labels={}):
        self.labels = labels
        self.children = set()

    def add_child(self, child):
        self.children.add(child)

    def name(self):
        return self.labels['spanID']

    def label(self):
        return self.labels['operationName']


    def __str__(self):
        return self.labels['spanID'] + '(' + ','.join(map(lambda x: str(x), self.children))  + ')'

    def todot(self, dot):
        dot.node(self.name(), self.label())
        for c in self.children:
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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.labels == other.labels
        else:
            return False

    def collapse(self):
        # this one is gonna be tricky
        new_node = CallGraph(self.labels)

        working = []
        for child in self.children:
            working.append(child)

        for child in working:
            if child == self:
                for c in child.children:
                    working.append(c)
            else:
                new_node.add_child(child.collapse) 

        return new_node
        




