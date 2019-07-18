class CallGraph():
    def __init__(self, labels={}):
        self.labels = labels
        self.children = set()

    def add_child(self, child):
        self.children.add(child)

    def name(self, rule):
        #return str(self.labels)
        return self.label(rule)

    def label(self, rule):
        #return self.labels.values()[0]
        #return str(self.labels)
        st = ''
        for k in self.labels:
            if k in rule or rule == []:
                print "DO EET " + k + " on " + str(rule)
                st += k + '=' + str(self.labels[k]) + ","


        return st

    def formula(self, rule=[]):
        print "RULE is " + str(rule)
        timeline = []
        names = map(lambda x: x.name(rule), self.children)
        for item in self.children:
            print "item " + str(item) + " LABELS be " + str(item.labels)
            timeline.append((item, "START", item.labels['startTime']))
            timeline.append((item, "END", item.labels['startTime'] + item.labels['duration']))

        timeline = sorted(timeline, key=lambda x: x[-1])
        ret = {}
        local = []
        for item in timeline:
            #ret += "(%s) before %s %s " % (", ".join(names), item[0].name(rule), item[1])
            local.append({'faults': names[:], 'before-anchor': item[0].name(rule), 'event': item[1]})
            if item[1] == "END":
                names.remove(item[0].name(rule))
        ret[self.name(rule)] = local
        for c in self.children:
            fm = c.formula(rule)
            for k in fm:
                ret[k] = fm[k]

        #return ret + ") AND ".join(map(lambda x: x.formula(rule), self.children))
        return ret



    def __str__(self):
        return str(self.labels) + '(' + ','.join(map(lambda x: str(x), self.children))  + ')'

    def todot(self, dot, rule=[]):
        dot.node(self.name(rule), self.label(rule))
        for c in self.children:
            print "c is " + str(c)
            c.todot(dot, rule)
            dot.edge(self.name(rule), c.name(rule))

    def transform(self, rules):
        new_labels = {}
        print "ROOLS " + str(rules)
        for item in self.labels:
            if item in rules:
                print "lam"
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
        




