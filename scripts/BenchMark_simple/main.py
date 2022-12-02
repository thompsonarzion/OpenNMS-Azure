from datetime import datetime
import os
import time
import argparse

from classes import opennms
from libraries import web_connector


opennms_server_ip_address = "localhost"
opennms_server_port = 8980

print("Server:", opennms_server_ip_address)
print("Port:", opennms_server_port)

ConnectionWrapper = web_connector.web_connector()
OpenNMS_Instance = opennms.Opennms(
    opennms_server_ip_address, opennms_server_port, ConnetionWrapper=ConnectionWrapper
)
OpenNMS_Instance.discover()


# print(OpenNMS_Instance.getAPIEndpoints())

# Add a single node with default value
# OpenNMS_Instance.addNode()

# Adds 150 random nodes
# OpenNMS_Instance.addRandomNodes(count=150)

# Force scanning the Nodes
# OpenNMS_Instance.Scan(True)

# Print the number of nodes
# print(OpenNMS_Instance.getNodes()["count"])

# Delete Node with ID = 1
# OpenNMS_Instance.deleteNode(1)

# Delete all Nodes
# OpenNMS_Instance.deleteAllNodes()

# print list of Requestions
# print(OpenNMS_Instance.listRequestions())

# print list Deployed Stats for Requestions
# print(OpenNMS_Instance.listRequestionsDeployedStats())

# Add a new Requestions
# print(OpenNMS_Instance.addRequisition("dogs"))

# Clean Requestions Detector Definition
# OpenNMS_Instance.clearRequisitionDefinitionDetectors("cats")

# Clean Requestions Policies Definition
# OpenNMS_Instance.clearRequisitionDefinitionPolicies("cats")

# Add Detector Definition to a Requestions
# OpenNMS_Instance.addRequisitionDefinitionDetector(
#    "cats", "ICMP2", "org.opennms.netmgt.provision.detector.icmp.IcmpDetector"
# )

# Add  Detector Definition to a Requestions
# OpenNMS_Instance.addRequisitionDefinitionDetector(
#    "cats",
#    "ICMP4",
#    "org.opennms.netmgt.provision.detector.icmp.IcmpDetector",
#    [{"key": "allowFragmentation", "value": "False"}, {"key": "port", "value": "133"}],
# )

# Delete a Requestion
# OpenNMS_Instance.deleteRequisition("cats")

# Get all events
# OpenNMS_Instance.get_all_events()

# Get events count
# OpenNMS_Instance.get_events_count()


#### Sample Script


def createNode(step, count=0, req="Benchmark"):
    print("" * 10)
    _start = datetime.now()
    print("STEP ", step, "-- Add", count, "Nodes")
    OpenNMS_Instance.addRandomNodes(count, req)
    print("Created", count, "nodes in ", datetime.now() - _start)
    OpenNMS_Instance.Scan(requisition=req)

    # Idea: we should check the requisition to see if all nodes are now in the 
    #       database (Under header "Nodes in Database")
    
    time.sleep(10)
    _start = datetime.now()
    print("STEP ", step, "-- Delete", count, "Nodes")
    OpenNMS_Instance.deleteAllNodes(req)
    # Assume localhost is always present, which means we should be left with 
    # 1 node after cleaning up the other nodes
    number_of_nodes=len(OpenNMS_Instance.getNodes(req)["node"])
    number_of_tries=0 
    while number_of_nodes > 1 and number_of_tries<30:
        for n in OpenNMS_Instance.getNodes(req)["node"]:
            if n["label"] !="localhost":
                OpenNMS_Instance.deleteNode(n["id"])
        time.sleep(number_of_tries) 
        number_of_tries+=5
        number_of_nodes=len(OpenNMS_Instance.getNodes(req)["node"])
    print("Attempted to delete", count, "nodes in ", datetime.now() - _start,"with ",(number_of_tries/5),"attempts")
    print("---" * 10)


_start = datetime.now()
print("STEP 1 -- Create Benchmark requisition")
print("Start:", _start)
OpenNMS_Instance.addRequisition("Benchmark")
_listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
found_benchmark_req = False
for a in _listRequestions:
    if "Benchmark" in a["foreign-source"]:
        found_benchmark_req = True
while not found_benchmark_req:
    _listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
    for a in _listRequestions:
        if "Benchmark" in a["foreign-source"]:
            found_benchmark_req = True
print("Created Benchmark requisition: ", datetime.now() - _start)

step_count = 2
for a in [10000, 100000]:
    createNode(step_count, a, "Benchmark")
    step_count += 1

_start = datetime.now()
print("STEP", step_count, "-- Delete/Cleanup Benchmark requisition")
OpenNMS_Instance.deleteRequisition("Benchmark")
_listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
for a in _listRequestions:
    if "Benchmark" in a["foreign-source"]:
        found_benchmark_req = True
while found_benchmark_req:
    _listRequestions = OpenNMS_Instance.listRequestions()["model-import"]
    for a in _listRequestions:
        if "Benchmark" not in a["foreign-source"]:
            found_benchmark_req = False
print("Deleted Benchmark requisition: ", datetime.now() - _start)

print()

print("Event logs:")

for l in OpenNMS_Instance.Eventslog():
    print("[" + l["DateTime"].strftime("%Y/%m/%d - %H:%M%S.%f") + "]:", l["message"])
