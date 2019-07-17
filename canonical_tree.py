class CallGraph():
    def __init__(self, labels={}):
        self.labels = labels
        self.children = set()

    def add_child(self, child):
        self.children.add(child)

    def name(self):
        return self.labels['spanID']


    def __str__(self):
        return self.labels['spanID'] + '(' + ','.join(map(lambda x: str(x), self.children))  + ')'

    def todot(self, dot):
        dot.node(self.name())
        for c in self.children:
            c.todot(dot)
            dot.edge(self.name(), c.name())
        




