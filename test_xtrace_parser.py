import json
import pytest
from xtrace_parser import XTraceParser

@pytest.fixture
def testdir():
    return "xtrace_data/"

def test_xtrace_edges(testdir):
    fnames = ["hdfs_trace.json", "ds_trace.json"]
    for name in fnames:
        ip_fpath = testdir + name
        trace = XTraceParser(ip_fpath)
        trace.process()

        f = open(ip_fpath, "r")
        json_data = json.load(f)
        f.close()

        # Count the number of parent events that are also events in the trace
        # to find the number of edges in the trace
        trace_data = json_data[0]["reports"]
        events = set(map(lambda x: x["EventID"], trace_data))
        num_edges = 0
        for span in trace_data:
            if not "ParentEventID" in span:
                continue
            parents = set(span["ParentEventID"])
            num_edges += len(parents.intersection(events))

        # Check that the number of edges before and after processing match
        assert(num_edges == len(trace.edges))
