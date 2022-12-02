from datetime import datetime
from library import web_connector
import datetime


HORIZON_SERVER_IP_ADDRESS = "localhost"
HORIZON_SERVER_PORT = "8980"
HORIZON_SERVER_URL = "http://" + HORIZON_SERVER_IP_ADDRESS + ":" + HORIZON_SERVER_PORT

HORIZON_DEFAULT_USERNAME = "admin"
HORIZON_DEFAULT_PASSWORD = "admin"
HORIZON_DEFAULT_LOGIN_URL = HORIZON_SERVER_URL + "/opennms/j_spring_security_check"

HORIZON_DEFAULT_REQUISITION = "selfmonitor"
HORIZON_DEFAULT_REQUISITION_URL = (
    HORIZON_SERVER_URL
    + "/opennms/rest/requisitions/"
    + HORIZON_DEFAULT_REQUISITION
    + "/nodes"
)
HORIZON_DEFAULT_REQUISITION_SCAN_URL = (
    HORIZON_SERVER_URL
    + "/opennms/rest/requisitions/"
    + HORIZON_DEFAULT_REQUISITION
    + "/import"
)
HORIZON_DEFAULT_REQUISITION_SCAN_EXISTING = False

INTERNAL_DEFAULT_HEADER = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
}

WEB_CONNECTOR = web_connector.web_connector()

# Login
Response = WEB_CONNECTOR.post(
    HORIZON_DEFAULT_LOGIN_URL,
    {"j_username": HORIZON_DEFAULT_USERNAME, "j_password": HORIZON_DEFAULT_PASSWORD},
    header=INTERNAL_DEFAULT_HEADER,
)
# print(Response)

TMP_HEADER = {}
TMP_HEADER["user-agent"] = INTERNAL_DEFAULT_HEADER["user-agent"]
TMP_HEADER["Accept"] = "application/json, text/plain, */*"
TMP_HEADER["Origin"] = HORIZON_SERVER_URL
TMP_HEADER["Referer"] = HORIZON_SERVER_URL + "/opennms/admin/ng-requisitions/index.jsp"
TMP_HEADER["Content-Type"] = "application/json;charset=UTF-8"
TMP_HEADER["Content-Length"] = "40"
TMP_HEADER["DNT"] = "1"

print("Pushing Nodes info to the server at", datetime.datetime.now())
start_count = 1
for ip in range(5000):
    Response = WEB_CONNECTOR.post(
        HORIZON_DEFAULT_REQUISITION_URL,
        '{"foreign-id":"'
        + str(start_count)
        + '","node-label":"Node-'
        + str(start_count)
        + '","interface":[{"ip-addr":"172.21.0.5","snmp-primary":"N","status":"1","meta-data":[],"monitored-service":[{"service-name":"ICMP","meta-data":[]}]}]}],"parent-foreign-id":null,"parent-node-label":null,"asset":[],"meta-data":[],"category":[]}',
        header=TMP_HEADER,
    )
    start_count += 1
print("Last node number:", start_count)
print("Complated pushing Nodes info to the server at", datetime.datetime.now())

print("Forcing a scan for newly added nodes at", datetime.datetime.now())
### Force a scan for <HORIZON_DEFAULT_REQUISITION> requisitions
Response = WEB_CONNECTOR.put(
    HORIZON_DEFAULT_REQUISITION_SCAN_URL,
    data="rescanExisting=" + str(HORIZON_DEFAULT_REQUISITION_SCAN_EXISTING),
    header=TMP_HEADER,
)
print("Completed forcing a scan for newly added nodes at", datetime.datetime.now())
