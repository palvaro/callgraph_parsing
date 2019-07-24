import re
import json
import logging
from graphviz import Digraph
from canonical_tree import CallGraph

logging.basicConfig(format='%(asctime)s - %(name)s '\
        '- %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('WARNING')

class CalTrace:
    def __init__(self, ip_file:str):
        self.svc_list = {}
        self.parent_list = {}
        self.svcs = {}
        self.roots = []
        self.trace_file = ip_file
        self.json_data = self.process()
    
    def process(self):
        f = open(self.trace_file, "r")
        self.json_data = json.load(f)
        f.close()
        self.parse_data()

    def get_uniq_svc(self, svc):
        """
        Response data is structured so that single pool has multiple JSON
        dictionaries. Select one for each pool and stick with it.
        """
        if svc.labels['pool'] not in self.svcs:
            self.svcs[svc.labels['pool']] = svc
        else:
            pool = svc.labels['pool'] 
            if svc.labels['startTime'] < self.svcs[pool].labels['startTime']:
                self.svcs[pool].labels['startTime'] = svc.labels['startTime']
            self.svcs[pool].labels['duration'] += svc.labels['duration']
            svc = self.svcs[pool]
        return svc

    def dont_process(self, svc, parent):
        """
        Return True if svc is not to be processed, else False
        """
        #if re.search('elasticsearch', svc.label, re.IGNORECASE):
        #    return True
        if parent.labels['pool'] == svc.labels['pool']:
            return True
        return False

    def create_service(self, labels):
        svc = CallGraph(labels)
        return svc

    def populate_roots(self):
        for pool in sorted(self.svcs.keys()):
            svc = self.svcs[pool]
            if not svc.parents:
                self.roots.append(svc)

    def create_tree(self):
        keys = list(self.svc_list.keys())
        for uniq_id in keys:
            cur_svc = self.svc_list[uniq_id]
            parent_id = self.parent_list[uniq_id]
            if parent_id not in self.svc_list:
                cur_svc = self.get_uniq_svc(cur_svc)
                logger.debug("Poolname is %s, %s not present", \
                        cur_svc.labels['pool'], parent_id)
                continue

            parent = self.svc_list[parent_id]
            if self.dont_process(cur_svc, parent):
                continue

            cur_svc = self.get_uniq_svc(cur_svc)
            parent = self.get_uniq_svc(parent)

            parent.add_child(cur_svc)
            cur_svc.add_parent(parent)
            logger.debug("Service name %s, Parent %s, pool %s", \
                    cur_svc.labels['name'], parent.labels['pool'], \
                    cur_svc.labels['pool'])
            logger.debug("Edge Created %s --> %s, Service endpoint is %s", \
                    parent.labels['pool'], cur_svc.labels['pool'], \
                    cur_svc.labels['name'])
        self.populate_roots()

    def parse_data(self):
        to_process = self.json_data['responseData']
        if not to_process:
            self.json_data = {}
            return
        for ind in range(len(to_process)):
            svc_details = to_process[ind]['dimensions']
            timing_details = to_process[ind]['dataPoints'][0]
            labels = {}
            labels['status'] = svc_details['status']
            labels['name'] = svc_details['name']
            labels['id'] = svc_details['id']
            labels['parentId'] = svc_details['parentId']
            labels['env'] = svc_details['env']
            labels['pool'] = svc_details['poolname']
            labels['thrd'] = svc_details['threadId']
            labels['startTime'] = int(timing_details[0])
            labels['duration'] = int(timing_details[1])
            svc = self.create_service(labels)
            uniq_id = labels['id']
            parent_id = labels['parentId']
            self.svc_list[uniq_id] = svc
            self.parent_list[uniq_id] = parent_id

        self.create_tree()
