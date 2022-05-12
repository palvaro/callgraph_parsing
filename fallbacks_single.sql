# create pass 1 table
create view badgraphs as
	select graph, c_from, c_to, ord
	from result
	where stat='fail';

# create pass 2 table
create view candidates as
	select distinct b.c_from, b.c_to, r.c_to
	from result r, badgraphs b
	where r.graph = b.graph
	and r.c_from = b.c_from
  and r.c_to != b.c_to
  and r.c_to != r.c_from
  and b.c_to != b.c_from
  and r.stat != 'fail'
	and CAST(r.ord as int) > CAST(b.ord as int);

# create pass 3 table
create view not_fallbacks as 
	select distinct r1.c_from, r1.c_to, r2.c_to 
	from badgraphs b, result r1, result r2
	where r1.graph = r2.graph
  and b.c_from = r1.c_from
  and b.c_to = r1.c_to
  and r1.stat != 'fail'
  and r2.c_from = r1.c_from
  and r2.c_to != r1.c_to
  and r2.stat != 'fail'
	and CAST(r2.ord as int) > CAST(r1.ord as int);

# create pass 4 table
create view fallbacks as
	select * 
	from candidates 
	except 
	select * 
	from not_fallbacks;

create view retries as
  select distinct b.c_from, b.c_to
  from result r, badgraphs b
  where r.graph = b.graph
  and r.c_from = b.c_from 
  and r.c_to = b.c_to
  and r.stat != 'fail'
  and CAST(r.ord as int) > CAST(b.ord as int);

