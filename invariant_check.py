from abstract_graphs import DAG, identity, index_of, simple_name
from jaeger_parser import JaegerParser, truncate_hs
import os, subprocess, sqlite3

traces = {
	'before':['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10'],
	'adsvc_down':['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10'],
	'frontend-adsvc_down':['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10'],
	'product_down':['t1','t2','t3','t4','t5'],
	'product-adsvc_down':['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10']
}

# does the call to adservice fail
adsvc_fail = """select svc_lbl, svc_val, op_lbl, op_val, st_lbl, st_val, time_lbl, time_val from abstracts 
where svc_lbl='serviceName' 
and svc_val='adservice'
and st_lbl='status.code'
and st_val<>'0'"""

# does a call from frontend to shipping service exist
# call if adsvc_fail returned results
shipping = """select * from edgelabels
where src_svc_lbl='serviceName' 
and src_svc_val='frontend' 
and dst_svc_lbl='serviceName' 
and dst_svc_val='shippingservice'"""

# if two nodes are siblings, check if the earlier call failed
# call if shipping returned results
# i cut out the startTime label otherwise intersection was empty
query = """select n1_svc_lbl, n1_svc_val, n1_op_lbl, n1_op_val, n1_st_lbl, n1_st_val, n2_svc_lbl, n2_svc_val, n2_op_lbl, n2_op_val, n2_st_lbl, n2_st_val from siblings
where CAST(n1_time_val as int) > CAST(n2_time_val as int)
and n2_st_val <> '0'"""

# connect to database and execute commands via sqlite3 module
# extend this to loop over all traces later
def query_db(trace):
	os.system('python3 sql_run.py FI_traces/hipster_shop/adsvc_down/t1.json > t1.sql')
	os.system('sqlite3 t1.db < t1.sql')
	conn = sqlite3.connect('/databases/t1.db')
	c = conn.cursor()
	c.execute() # exectute hipstershop.sql script
	c.fetchall()

# execute commands via opening pipe to sqlite3 shell
# loop over all traces
def query_all(traces):
	outputs = []
	for fault in traces.keys():
		for trace in traces[fault]:
			os.system('python3 sql_run.py FI_traces/hipster_shop/'+fault+'/'+trace+'.json > '+fault+'_'+trace+'.sql')
			t = '.read ' + fault + '_' + trace + '.sql'
			command = 'sqlite3 :memory: "' + t + '" ".read hipstershop_views.sql" "' + adsvc_fail + '"'
			r = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
			output = r.communicate()
			if len(output[0])!= 0:
				command2 = 'sqlite3 :memory: "' + t + '" ".read hipstershop_views.sql" "' + shipping + '"'
				r = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True)
				output = r.communicate()
				if len(output[0]) != 0:
					command3 = 'sqlite3 :memory: "' + t + '" ".read hipstershop_views.sql" "' + query + '"'
					r = subprocess.Popen(command3, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
					output = r.communicate()
					outputs.append(output[0])
	#print(outputs)
	return outputs

# compute intersection of results over all traces
# prints set containing all rows in the intersection, 
# where each row is a pair of sibling nodes according to above query
def intersect(traces):	
	outputs = query_all(traces)
	p = {}
	for idx, item in enumerate(outputs):
		item = str(item)
		item = item.split('\n')
		p[idx] = set(item)
	for i in range(len(p)):
		result = p[0].intersection(p[i])
		p[0] = result
	print(result)
	return result


if __name__ == '__main__':
	intersect(traces)
	






