# callgraph simplification

Ellie test...!

The CallGraph class is a generic representation of a (tree-shaped, at least for now) trace.  Nodes are bags of flat labels,
and an edge from node A to node B indicates that depends causally on B.

CallGraphs can be converted from a concrete, raw representation into a variety of abstract representations, in order to simplify comparing or visualizing
individual graphs.  This proceeds in two phases:

 * A mapping phase, in which labels are omitted or transformed into an abstract domain.  In this phase we can do things like dropping timestamps and unique identifiers, converting ephemeral ports to integers, etc.  We can also flexibly experiment with different candidate labelings.

*  A reduction phase, in which the structure of the graph itself is simplified to elide redundant nodes.

Together, these steps can simplify a variety of common graph mutation tasks in our workflows.

For example, consider the common problem of converting a raw Jaeger trace, whose spans are method calls, into a smaller graph whose nodes represent
services and whose edges represent dependencies.

Step 1: Parse a Jaeger graph into the common representation.

    p = JaegerParser("trace.json")
    root = p.process()

Step 2: project out just the labels we care about; in this simple case, just the service name

    rules1 = {
        'serviceName' : 'lambda x : x',
    }
    new_root = root.transform(rules1)

Step 3: simplify the graph so that adjacent, similarly-labeled nodes collapse into one:

    collapsed_root = new_root.collapse() 


Here is a more complicated example, in which we retain some fields (timing info) for analysis, but define similarity w.r.t. collapsing
only in terms of one label:

    rules2 = {
        'serviceName' : 'lambda x : x',
        'startTime' : 'lambda x : x',
        'duration' : 'lambda x : x',
    }
    tree = root.transform(rules2).collapse(['serviceName'])


Take a look at the Jupyter notebook for examples and pictures.

# Theory

Note that in all of these examples I am doing something trivial in the rule map.  I am 

 1) selecting a few fields, and implictly ignoring many others, and
 2) supplying the identity function as a lambda.

Consider how (2) is going to generalize.  It is an abstraction function, mapping from a concrete domain into an abstract domain in which (hopefully) things that are "the same" can be meaningfully compared.  The two extreme cases are the identity function and the bottom function (implicitly defined for every label not mentioned in a rule map).  If everything is mapped to the identity function, an abstract trace is identical to its concrete trace (and hence no two abstract traces are the same).  If everything is mapped to bottom all abstract traces are identical but they contain no information.

What other kinds of abstraction functions are there?  There are presumably those that forget *some* of their input information (e.g., by truncating the input). Perhaps most interesting (to me) are the order-preserving abstraction functions we might implement.  For example:

 * A function that maps from the domain of ephemeral ports to the domain of (0, 1, [...]) representing the order in which those ports were allocated.
 * The same thing for process ids, thread ids, event ids, etc.
 * A similar thing for real time

Given a set of mapping function supplied by the user (one for each node label, at least implicitly), what properties do we want to assert about the functions?  Can we check these properties?
