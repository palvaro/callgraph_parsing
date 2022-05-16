# -------- SQL VIEWS FOR HIPSTERSHOP -------- #

# join nodelabels for serviceName, operationName, status.code, startTime
create view abstracts as 
	select l1.node idx, l1.label svc_lbl, l1.value svc_val, l3.label st_lbl, l3.value st_val, l4.label time_lbl, l4.value time_val
	from nodelabels l1
	inner join nodelabels l3
	inner join nodelabels l4
	on l1.node=l3.node and l1.node=l4.node and l3.node=l4.node
	and l1.label='serviceName' 
	and l3.label='status.code'
	and l4.label='startTime';	 	 

# edge table with labels & values
create view edgelabels as
	select n1.svc_lbl src_svc_lbl, n1.svc_val src_svc_val, n1.st_lbl src_st_lbl, n1.st_val src_st_val, n1.time_lbl src_time_lbl, n1.time_val src_time_val, n2.svc_lbl dst_svc_lbl, n2.svc_val dst_svc_val,  n2.st_lbl dst_st_lbl, n2.st_val dst_st_val, n2.time_lbl dst_time_lbl, n2.time_val dst_time_val
	from edge
	inner join abstracts n1
	on edge.src = n1.idx
	inner join abstracts n2
	on edge.dst = n2.idx;	

# table of pairs of sibling nodes
create view siblings as
    select e1.dst_svc_lbl n1_svc_lbl, e1.dst_svc_val n1_svc_val, e1.dst_st_lbl n1_st_lbl, e1.dst_st_val n1_st_val, e1.dst_time_lbl n1_time_lbl, e1.dst_time_val n1_time_val, e2.dst_svc_lbl n2_svc_lbl, e2.dst_svc_val n2_svc_val, e2.dst_st_lbl n2_st_lbl, e2.dst_st_val n2_st_val, e2.dst_time_lbl n2_time_lbl, e2.dst_time_val n2_time_val
    from edgelabels e1
    inner join edgelabels e2
    on e1.src_svc_lbl = e2.src_svc_lbl
    and e1.src_svc_val = e2.src_svc_val
    and e1.src_st_lbl = e2.src_st_lbl
    and e1.src_st_val = e2.src_st_val
    and e1.src_time_lbl = e2.src_time_lbl
    and e1.src_time_val = e2.src_time_val
    and e1.dst_time_val <> e2.dst_time_val;

# table of failed calls    
create view fails as 
	select svc_lbl, svc_val, st_lbl, st_val, time_lbl, time_val 
	from abstracts 
	where st_lbl='status.code'
	and st_val<>'0';

# get info for table of tuples G1, G2,...
create view ordering as
	select src_svc_val as src_id, src_st_val, src_time_val, dst_svc_val as dst_id, dst_st_val, dst_time_val
	from edgelabels
	order by dst_time_val;

# create table of tuples G1, G2,...
create view calls as 
	select src_id, dst_id, dst_time_val, dst_st_val
	from ordering;









