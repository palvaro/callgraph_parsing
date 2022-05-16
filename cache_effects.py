from abstract_graphs import DAG, identity, index_of, simple_name
from jaeger_parser import JaegerParser
import os, subprocess, sqlite3
import re

traces = {
        'cache_effects': ['trace_1', 'trace_2', 'trace_3', 'trace_4', 'trace_5',\
                'trace_6', 'trace_7', 'trace_8', 'trace_8', 'trace_9', \
                'trace_10', 'trace_11', 'trace_12', 'trace_13', 'trace_14']
        }

# get list of calls
metaquery = """select * from calls"""

# execute commands via opening pipe to sqlite3 shell & loop over all traces
def metaquery_all(traces):
    result = {}
    for fault in traces.keys():
        for trace in traces[fault]:
            os.system('python3 sql_run.py ' + fault + '/' + trace+'.json > '+fault+'_'+trace+'.sql')
            t = '.read ' + fault + '_' + trace + '.sql'
            command = 'sqlite3 :memory: "' + t + '" ".read svcop_views.sql" "' + metaquery + '"'
            r = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output = r.communicate()
            #print(fault, trace)
            graph = fault + '_' + trace
            output_list = output[0].splitlines()
            result[graph] = []
            for i in output_list:
                i = i.decode('utf-8')
                data = i.split('|')
                if data[3] == '0':
                    data[3] = 'success'
                elif data[3] == '-1':
                    data[3] = 'unknown'
                else:
                    data[3] = 'fail'
                c = (graph, data[0],data[1],int(data[2]),data[3])
                result[graph].append(c)
    #print(result)
    return result

def process(traces, outfile):
    # execute metaquery
    result = metaquery_all(traces)
    # convert result into list of dicts
    reslst = []
    for g in result.keys():
        for c in result[g]:
            d = {}
            d['graph'] = c[0]
            d['c_from'] = c[1]
            d['c_to'] = c[2]
            d['ord'] = c[3]
            d['stat'] = c[4]
            reslst.append(d)
    #print(reslst)
    # write as a new sql db
    table = """create table result (
        graph text,
        c_from text,
        c_to text,
        ord text,
        stat text
    );"""
    f = open(outfile,'a')
    f.write(table+'\n')
    for d in reslst:	
        cols = ', '.join("'"+str(x).replace('/','_')+"'" for x in d.keys())
        vals = ', '.join("'"+str(x).replace('/','_')+"'" for x in d.values())
        ins = "INSERT INTO %s (%s) VALUES (%s);" %('result',cols,vals)	
        f = open(outfile,'a')
        f.write(ins+'\n')

    f.close()	

# takes as input file of sql inserts
def query_all(sql_file):
    # input sql insert file into sqlite & execute pass 1
    t = '.read ' + sql_file
    p1 = """select * from candidates"""
    command = 'sqlite3 :memory: "' + t + '" ".read cache.sql" "' + p1 + '"'
    r = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output = r.communicate()
    print("Fallbacks")
    fallbacks = (output[0].decode('utf-8')).split('\\n')
    for f in fallbacks:
        print(f)

if __name__=='__main__':
    process(traces,'result.sql')
    query_all('result.sql')
    os.system('rm result.sql')
