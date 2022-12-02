# importing the multiprocessing module
import multiprocessing
from datetime import datetime
import logging
import sys

from classes import opennms
from libraries import web_connector
import sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def createNode(OpenNMS_Instance,count, req="Benchmark"):
    OpenNMS_Instance.deleteRequisition("selfmonitor")
    logging.info("" * 10)
    _start = datetime.now()
    logging.info("[p1] -- Add "+str(count)+" Nodes")
    OpenNMS_Instance.addRandomNodes(count, req)
    logging.info("[p1] Created "+str(count)+" nodes in "+ str(datetime.now() - _start))
    OpenNMS_Instance.Scan(requisition=req)
    
  
def add_nodes(num,OpenNMS_Instance):
    """
    function to add num of nodes
    """
    _start = datetime.now()
    requisition_name="Benchmark"+str(num)
    OpenNMS_Instance.addRequisition(requisition_name)
    _listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
    found_benchmark_req = False
    for a in _listRequestions:
        if requisition_name in a["foreign-source"]:
            found_benchmark_req = True
    while not found_benchmark_req:
        _listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
        for a in _listRequestions:
            if requisition_name in a["foreign-source"]:
                found_benchmark_req = True
    logging.info("Created Benchmark requisition: "+str(datetime.now() - _start))

    createNode(OpenNMS_Instance,num, requisition_name)
    sys.exit(0)


def query_nodes(num,OpenNMS_Instance):
    requisition_name="Benchmark"+str(num)
    found_benchmark_req=False
    _start = datetime.now()
    while not found_benchmark_req:       
        _listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
        for a in _listRequestions:
            if requisition_name in a["foreign-source"]:
                found_benchmark_req = True
    while found_benchmark_req:
        _data=OpenNMS_Instance.getRequisition(requisition_name)
        num_nodes=len(_data['node'])
        if num_nodes == num and _data["last-import"] is not None:
            logging.info("[p2] Number of Nodes in Requisition found to match ("+str(num_nodes)+") after "+str(datetime.now() - _start))
            sys.exit(0)

def query_stats(num,OpenNMS_Instance):
    _data=OpenNMS_Instance.listRequestionsDeployedStats()
    requisition_name="Benchmark"+str(num)
    requisition_found=False
    _start = datetime.now()
    while not requisition_found:
        try:
            _data=OpenNMS_Instance.listRequestionsDeployedStats()
        except:
            _data=OpenNMS_Instance.listRequestionsDeployedStats()
        for req in _data["foreign-source"]:
            if req["name"] == requisition_name:
                requisition_found=True
    logging.info("[p3] Took "+str(datetime.now() - _start)+" to find the requisition")

    _start = datetime.now()
    while requisition_found:
        _data=OpenNMS_Instance.listRequestionsDeployedStats()
        for req in _data["foreign-source"]:
            if req["totalCount"] == num:
                requisition_found=False
    logging.info("[p3] Took "+str(datetime.now() - _start)+" for the totalCount to match our expected value ("+str(num)+")")

        

    



if __name__ == "__main__":
    opennms_server_ip_address = "localhost"
    opennms_server_port = "8980"
    

    ConnectionWrapper = web_connector.web_connector()
    OpenNMS_Instance = opennms.Opennms(
        opennms_server_ip_address, opennms_server_port, ConnetionWrapper=ConnectionWrapper
    )
    OpenNMS_Instance.discover()



    # creating processes
    numberofNodes=int(sys.argv[1])
    p1 = multiprocessing.Process(target=add_nodes, args=(numberofNodes,OpenNMS_Instance, ))
    p2 = multiprocessing.Process(target=query_nodes, args=(numberofNodes,OpenNMS_Instance, ))
    p3 = multiprocessing.Process(target=query_stats, args=(numberofNodes,OpenNMS_Instance, ))
  
    # starting process 1
    p1.start()
    # starting process 2
    p2.start()
    # starting process 3
    p3.start()

    while p1.is_alive() or p2.is_alive() or p3.is_alive():
        pass
  
    # both processes finished
    print("Done!")
