# create pass 1 table
create view twographs as
	select distinct r1.graph as g1, r2.graph as g2
	from result r1, result r2
	where r1.graph != r2.graph;

# create pass 2 table
create view candidates as
	select distinct t.g1 || t.g2 as name, r1.c_from as fr, r1.c_to as t, r2.c_to as f
  from result r1, result r2, twographs t
  where r1.graph = t.g1
  and r2.graph = t.g2
  and r1.c_from = r2.c_from
  and r1.c_to NOT IN (select c_to from result where result.graph=t.g2)
  and r2.c_to NOT IN (select c_to from result where result.graph=t.g1);

create view counts as 
  select count(*) as occ, fr, t, f 
  from candidates
  group by fr, t, f;

create view fallbacks as
  select c.fr, c.t, c.f
  from counts as c
  where c.occ >= (select ifnull((select sum(occ) from counts where fr = c.fr and t = c.t and f != c.f), 0));
