# -------- SQL QUERIES FOR BOOKINFO -------- #

# ---- VIEWS ---- #

# repopulate edge table w/label & value names, save as modifiededge
create view modifiededge as
select n1.label src_lbl, n1.value src_val, n2.label dst_lbl, n2.value dst_val
from edge
inner join nodelabels n1
on edge.src = n1.node
inner join nodelabels n2
on edge.dst = n2.node;

# join nodelabels tables for serviceName & process-ip
# need to load a .sql db with serviceName & process-ip for a given trace
create view svc_ip as 
select l1.label svc_lbl, l1.value svc_val, l2.label ip_lbl, l2.value ip_val
from nodelabels l1
inner join nodelabels l2
on l1.node=l2.node
and l1.label<>l2.label and l1.value<>l2.value
and l1.label='serviceName' and l2.label='process-ip';

# ---- CHARACTERIZE DIFFERENT FAULTS ---- #

# see if node serviceName=ratings exists:
select * from nodelabels where label='serviceName' and value='ratings.default';

# see if node serviceName=reviews exists:
select * from nodelabels where label='serviceName' and value='reviews.default';

# see if edge from reviews to ratings exists:
select * from label_reach where f_lbl='serviceName' and f_val='reviews.default' and t_lbl='serviceName' and t_val='ratings.default';

# see if edge from productpage to reviews exists:
select * from label_reach where f_lbl='serviceName' and f_val='productpage.default' and t_lbl='serviceName' and t_val='reviews.default';





