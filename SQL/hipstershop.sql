# -------- SQL QUERIES FOR HIPSTERSHOP -------- #

# ---- CREATE VIEWS ---- #

# join nodelabels for serviceName, status.code, startTime
create view abstracts as 
	select l1.node idx, l1.label svc_lbl, l1.value svc_val, l2.label st_lbl, l2.value st_val, l3.label time_lbl, l3.value time_val
	from nodelabels l1
	inner join nodelabels l2
	inner join nodelabels l3
	on l1.node=l2.node and l1.node=l3.node and l2.node=l3.node
	and l1.label='serviceName' 
	and l2.label='status.code'
	and l3.label='startTime'
	group by l1.node, l1.label, l1.value, l2.label, l2.value, l3.label, l3.value
	having count(*)>1;	 	 

# create edge table with labels & values
create view edgelabels as
	select n1.svc_lbl src_svc_lbl, n1.svc_val src_svc_val, n1.st_lbl src_st_lbl, n1.st_val src_st_val, n1.time_lbl src_time_lbl, n1.time_val src_time_val, n2.svc_lbl dst_svc_lbl, n2.svc_val dst_svc_val, n2.st_lbl dst_st_lbl, n2.st_val dst_st_val, n2.time_lbl dst_time_lbl, n2.time_val dst_time_val
	from edge
	inner join abstracts n1
	on edge.src = n1.idx
	inner join abstracts n2
	on edge.dst = n2.idx;
	group by n1.svc_lbl, n1.svc_val, n1.st_lbl, n1.st_val, n1.time_lbl, n1.time_val, n2.svc_lbl, n2.svc_val, n2.st_lbl, n2.st_val, n2.time_lbl, n2.time_val
	having count(*)>1;	

# get all pairs of sibling nodes
create view sib_nodes as
    select e1.dst_lbl lbl1, e1.dst_val val1, e2.dst_lbl lbl2, e2.dst_val val2
    from edgelabels e1
    inner join edgelabels e2
    on e1.src_lbl = e2.src_lbl
    and e1.src_val = e2.src_val;

# ---- CHECK FOR FEATURES ---- #

# does a call from frontend to shipping service exist
select * from edgelabels
where src_lbl='serviceName' and src_val='frontend' 
and dst_lbl='serviceName' and dst_val='shippingservice'; 

# does a call from frontend to adservice exist 
select * from label_reach
where f_lbl='serviceName' and f_val='frontend' 
and t_lbl='serviceName' and t_val='adservice';  

select * from abstracts
where svc_lbl='serviceName' and svc_val='frontend'
and st_lbl='status.code' and st_val<>'0';

# if two nodes are siblings, check if the earlier call failed
select * from sib_nodes
where 












