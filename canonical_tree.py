import re
class CallGraph():
    def __init__(self, labels={}):
        self.labels = labels
        self.children = set()
        self.parents = set()

    def add_child(self, child):
        self.children.add(child)

    def add_parent(self, parent):
        self.parents.add(parent)

    def name(self, rule):
        #return str(self.labels)
        return self.label(rule)

    def label(self, rule):
        #return self.labels.values()[0]
        #return str(self.labels)
        st = ''
        for k in self.labels:
            if k in rule or rule == []:
                st += k + '=' + str(self.labels[k]) + ","

        return st

    def nodes(self):
        cnt = 1
        for c in self.children:
            cnt += c.nodes()
        return cnt

    def depth(self):
        max = 0
        for c in self.children:
            if c.depth() > max:
                max = c.depth()
        return max + 1
        
    def label_values(self):
        # return a map of label => [ values ]
        #lbls = self.labels.copy()   
        lbls = {}
        for l in self.labels:
            lbls[l] = [ self.labels[l] ]
        for c in self.children:
            ch = c.label_values()
            for k in ch:
                if k not in lbls:
                    lbls[k] = ch[k]
                else:
                    lbls[k] = lbls[k] + ch[k]

        return lbls

    def formula(self, rule=[]):
        timeline = []
        names = list(map(lambda x: x.name(rule), self.children))
        for item in self.children:
            timeline.append((item, "START", item.labels['startTime']))
            timeline.append((item, "END", item.labels['startTime'] + item.labels['duration']))

        timeline = sorted(timeline, key=lambda x: x[-1])
        ret = {}
        local = []
        for item in timeline:
            #ret += "(%s) before %s %s " % (", ".join(names), item[0].name(rule), item[1])
            #print("item is %s, type %s" % (item, type(item)))

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
            c.todot(dot, rule)
            dot.edge(self.name(rule), c.name(rule))

    def transform(self, rules, totality={}):
        new_labels = {}
        if 'transform' in rules and 'excise' in rules:
            xform = rules['transform']
        else:
            # for backwards compatibility while I play
            xform = rules
    
        for item in self.labels:
            if item in xform:
                # forgive me for this!
                #exec("lmb = " + rules[item])
                #lmb = eval(xform[item])
                #new_labels[item] = lmb(self.labels[item], totality.get(item, []))
                if item not in totality:
                    print("%s is missing from map!" % item)
                new_labels[item] = xform[item](self.labels[item], totality.get(item, []))
       
            #print("ITREM %s" % item) 
            if 'excise' in rules and item in rules['excise']:
                #lmb = eval(rules['excise'][item])
                #if lmb(self.labels[item]):
                if rules['excise'][item](self.labels[item]):
                    new_labels = {} 

        new_node = CallGraph(new_labels)
        for c in self.children:
            new_node.add_child(c.transform(rules, totality))

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
            if child.label(rule) == "" or child.equiv(self, rule):
                for c in child.children:
                    working.append(c)
            else:
                new_node.add_child(child.collapse(rule)) 

        return new_node
        




