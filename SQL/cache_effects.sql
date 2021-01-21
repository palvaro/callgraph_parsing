# -------- SQL QUERIES FOR CACHE TRACES -------- #

# ---- VIEWS ---- #

create view modifiededge as
    select n1.label src_lbl, n1.value src_val, n2.label dst_lbl, n2.value dst_val
    from edge
    inner join nodelabels n1
    on edge.src = n1.node
    inner join nodelabels n2
    on edge.dst = n2.node;

create view details as 
    select edge.src src, n1.value op1, edge.dst dst, n2.value op2
    from edge
    inner join nodelabels n1
    on edge.src = n1.node
    inner join nodelabels n2
    on edge.dst = n2.node
    and n1.label='operationName' and n2.label='operationName'; 
    
create view siblings as
    select d1.dst n1, d2.dst n2
    from details d1
    inner join details d2
    on d1.src = d2.src
    and d1.op2='MmcGet' and d2.op2='MmcSet';

create view operation_time as 
    select l1.node n, l1.label st_lbl, l1.value st_val, l2.label o_lbl, l2.value o_val
    from nodelabels l1
    inner join nodelabels l2
    on l1.node=l2.node
    and l1.label<>l2.label and l1.value<>l2.value
    and l1.label='startTime' and l2.label='operationName';

create view get_set as
    select op1.n n1, op1.st_val t1, op2.n n2, op2.st_val t2
    from operation_time op1
    inner join operation_time op2
    on op1.o_val='MmcGet' and op2.o_val='MmcSet';

create view result as
    select gs.n1, gs.n2
    from get_set gs
    inner join siblings s
    on gs.n1=s.n1 and gs.n2=s.n2
    and CAST(gs.t1 as int) < CAST(gs.t2 as int);

# ---- CHARACTERIZATION OF CACHE HIT ---- #

# assert that get is always terminal- this should return no entries:
select * from label_reach where f_lbl='operationName' and f_val='Get'; 

# assert that there are no set nodes- this should return no entries: 
select * from nodelabels where label='operationName' and value='MmcSet';

# ---- CHARACTERIZATION OF CACHE MISS ---- #

# assert that set and get have the same parent:
select * from modifiededge e1, modifiededge e2
where e1.dst_val='MmcGet' and e2.dst_val='MmcSet'
and e1.src_lbl=e2.src_lbl
and e1.src_val=e2.src_val;

# assert that get happens temporally before set:
select st_val1, st_val2, o_val1, o_val2
from operation_time
where o_val1='MmcGet' and o_val2='MmcSet'
and st_val1<st_val2; 




