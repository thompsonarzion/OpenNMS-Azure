import datetime, json


class Opennms:
    EVENT_LOGGER = []
    CONNECTION_WRAPPER = None
    SERVER_IP = ""
    SERVER_PORT = ""
    SERVER_WEB_URL = ""
    SERVER_USERNAME = ""
    SERVER_PASSWORD = ""
    SERVER_API_URL = "http://" + SERVER_IP + ":" + SERVER_PORT + "/opennms/api/v2"
    SERVER_API_ENDPOINTS = (
        "http://" + SERVER_IP + ":" + SERVER_PORT + "/opennms/api/v2/openapi.json"
    )

    DEFAULT_HEADER = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }

    # Random Section
    LOGGED_IN = False

    def _LogEvent(self, msg):
        self.EVENT_LOGGER.append(
            {"DateTime": datetime.datetime.now(), "message": str(msg)}
        )

    def Eventslog(self):
        return self.EVENT_LOGGER

    def __init__(
        self,
        ip_address,
        port,
        username="admin",
        password="admin",
        ConnetionWrapper=None,
    ) -> None:
        self.SERVER_IP = ip_address
        self.SERVER_PORT = port
        self.SERVER_WEB_URL = "http://" + self.SERVER_IP + ":" + self.SERVER_PORT
        self.SERVER_USERNAME = username
        self.SERVER_PASSWORD = password
        self.CONNECTION_WRAPPER = ConnetionWrapper

    def _ping(self):
        self._LogEvent("Running _ping method")
        _success = False
        _url = self.SERVER_WEB_URL + "/opennms/index.jsp"
        if not self.LOGGED_IN:
            self._LogEvent("User is not logged in, calling _login method")
            self._login()
        _result = self.CONNECTION_WRAPPER.get(_url)
        if _result.status_code == 302:
            self._LogEvent(
                "When attempting to ping ["
                + _url
                + "] we got redirected to ["
                + _result.headers["Location"]
                + "!"
            )
            print(_result.headers["Location"])
            _success = False
        elif _result.status_code == 200:
            _success = True

        self._LogEvent("Elapsed Time for _ping:" + str(_result.elapsed))
        return _success

    def _login(self) -> None:
        self._LogEvent("Running _login method")
        _url = self.SERVER_WEB_URL + "/opennms/j_spring_security_check"
        _result = self.CONNECTION_WRAPPER.post(
            _url,
            {"j_username": self.SERVER_USERNAME, "j_password": self.SERVER_PASSWORD},
            header=self.DEFAULT_HEADER,
        )
        self._LogEvent("Elapsed Time for _login:" + str(_result.elapsed))
        if _result.status_code == 200:
            self._LogEvent("Logging in was successul")
            self.LOGGED_IN = True
        else:
            self._LogEvent("Logging in was not successul")
            raise Exception("Failed to Login")

    def _disable_datachoice(self):
        _url = self.SERVER_WEB_URL + "/opennms/rest/datachoices"
        _data = {"action": "disable"}
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["Content-Type"] = "application/json;charset=UTF-8"
        _header["Content-Length"] = str(len(_data))
        _header["DNT"] = "1"

        _result = self.CONNECTION_WRAPPER.post(_url, _data, header=_header)
        self._LogEvent("Elapsed Time for _disable_datachoice:" + str(_result.elapsed))
        if _result.status_code != 204:
            self._LogEvent("Failed to disable data choice")
            raise Exception("Failed to disable data choice")

    def _info(self):
        if not self.LOGGED_IN:
            self._LogEvent("User is not logged in, calling _login method")
            self._login()
        _url = self.SERVER_WEB_URL + "/opennms/rest/info"
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = self.SERVER_WEB_URL + "/opennms/admin/sysconfig.jsp"
        _header["Content-Type"] = "application/json;charset=UTF-8"
        _header["DNT"] = "1"

        _result = self.CONNECTION_WRAPPER.get(_url, header=_header)
        self._LogEvent("Elapsed Time for _info:" + str(_result.elapsed))
        if _result.status_code != 200:
            self._LogEvent("Failed to get server info")
            raise Exception("Failed to get server info")
        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        return output["response"]

    def discover(self) -> None:
        self._LogEvent("Running discover method")
        if not self._ping():
            self._LogEvent("Unable to validate servers information!")
            raise Exception("Unable to validate servers information!")

        self.SERVER_API_URL = (
            "http://" + self.SERVER_IP + ":" + self.SERVER_PORT + "/opennms/api/v2"
        )
        self.SERVER_API_ENDPOINTS = (
            "http://"
            + self.SERVER_IP
            + ":"
            + self.SERVER_PORT
            + "/opennms/api/v2/openapi.json"
        )

        server_info = self._info()
        print("OpenNMS Version:" + server_info["displayVersion"])
        self._LogEvent("OpenNMS Version:" + server_info["displayVersion"])

    def getAPIEndpoints(self) -> dict:
        """
        Get the API Endpoints supported by OpenNMS Server
        """
        self._LogEvent("Running getAPIEndpoints method")
        return self.CONNECTION_WRAPPER.get(self.SERVER_API_ENDPOINTS).json()

    def Scan(self, rescanExisting=False, requisition="selfmonitor"):
        """
        Run rescan
        """
        self._LogEvent("Running getNodes method")
        if not self.LOGGED_IN:
            self._LogEvent("Not logged in!")
            raise Exception("Not logged in!")

        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"

        _url = (
            self.SERVER_WEB_URL
            + "/opennms/rest/requisitions/"
            + requisition
            + "/import"
        )
        _data = "rescanExisting=" + str(rescanExisting)
        _result = self.CONNECTION_WRAPPER.put(_url, data=_data, header=_header)
        self._LogEvent("Elapsed Time for getNodes:" + str(_result.elapsed))
        if _result.status_code != 202:
            self._LogEvent("Failed to request a scan")
            raise Exception("Failed to request a scan")

    #                      #
    # --> NODE METHODS <-- #
    #                      #
    def getNodes(self, requisition="selfmonitor"):
        """
        Gets the list of Nodes in a requisition
        """
        self._LogEvent("Running getNodes method")
        if not self.LOGGED_IN:
            self._LogEvent("Not logged in!")
            raise Exception("Not logged in!")
        _url = (
            self.SERVER_WEB_URL + "/opennms/rest/nodes"
        )


        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"

        _result = self.CONNECTION_WRAPPER.get(_url, header=_header)
        self._LogEvent("Elapsed Time for getNodes:" + str(_result.elapsed))
        if _result.status_code == 200:
            output = {}
            output["response"] = _result.json()
            output["elapsed"] = _result.elapsed
            return output["response"]
        else:
            self._LogEvent("Failed to get list of nodes in " + requisition)
            raise Exception("Failed to get list of nodes in " + requisition)

    def addNode(
        self,
        foreign_id="1",
        node_label="Node-0",
        ip_address="localhost",
        snmp_primary="N",
        requisition="selfmonitor",
    ):
        """
        Add a node to OpenNMS Server
        """
        self._LogEvent("Running addNode method")
        if not self.LOGGED_IN:
            self._LogEvent("Not logged in!")
            raise Exception("Not logged in!")
        _url = (
            self.SERVER_WEB_URL + "/opennms/rest/requisitions/" + requisition + "/nodes"
        )
        _data = (
            '{"foreign-id":"'
            + str(foreign_id)
            + '","node-label":"'
            + node_label
            + '","interface":[{"ip-addr":"'
            + ip_address
            + '","snmp-primary":"'
            + snmp_primary
            + '","status":"1","meta-data":[],"monitored-service":[{"service-name":"ICMP","meta-data":[]}]}]}],"parent-foreign-id":null,"parent-node-label":null,"asset":[],"meta-data":[],"category":[{"name":"Servers"}]}'
        )

        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["Content-Type"] = "application/json;charset=UTF-8"
        _header["Content-Length"] = str(len(_data))
        _header["DNT"] = "1"

        _result = self.CONNECTION_WRAPPER.post(_url, _data, header=_header)
        self._LogEvent("Elapsed Time for addNode:" + str(_result.elapsed))
        if _result.status_code != 202:
            self._LogEvent("Failed to add a node")
            raise Exception("Failed to add a node")

    def addRandomNodes(self, count=1, requisition="selfmonitor"):
        """
        Add random number of Nodes to OpenNMS Server
        """
        self._LogEvent("Running AddRandomNodes method")
        if not self.LOGGED_IN:
            self._LogEvent("Not logged in!")
            raise Exception("Not logged in!")

        for n in range(count):
            self.addNode(
                foreign_id=n, node_label="Node-" + str(n), requisition=requisition
            )

    def deleteNode(self, id, requisition="selfmonitor"):
        """
        Deletes a Node
        """
        self._LogEvent("Running deleteNode method")
        _url = (
            self.SERVER_WEB_URL
            + "/opennms/rest/nodes/"
            + str(id)
        )
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.delete(_url, _header)
        self._LogEvent("Elapsed Time for deleteNode:" + str(_result.elapsed))
        if _result.status_code != 202:
            self._LogEvent("Failed to delete node with id " + str(id))
            raise Exception("Failed to delete node with id " + str(id))

    def deleteAllNodes(self, requisition="selfmonitor"):
        """
        Delete Nodes
        """
        self._LogEvent("Running deleteAllNodes method")
        # Get Nodes
        _nodes = self.getNodes(requisition)

        # Delete them one by one
        for n in _nodes["node"]:
            self.deleteNode(id=n["id"], requisition=requisition)

        # We need to force the synchronization so the DB is updated
        self.Scan(True)

    #                             #
    # --> REQUISITION METHODS <-- #
    #                             #
    def listRequestions(self):
        """
        List Requestions
        """
        self._LogEvent("Running listRequestions method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/requisitions"
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.get(_url, _header)

        if _result.status_code != 200:
            self._LogEvent("Failed retrieve requestion list")
            raise Exception("Failed retrieve requestion list")
        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        self._LogEvent("Elapsed Time for listRequestions:" + str(output["elapsed"]))

        return output["response"]

    def listRequestionsDeployedStats(self):
        """
        List Deployed Stats for Requestions
        """
        self._LogEvent("Running listRequestions method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/requisitions/deployed/stats"
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.get(_url, _header)

        if _result.status_code != 200:
            self._LogEvent("Failed retrieve stats for requestion list")
            raise Exception("Failed retrieve stats for requestion list")

        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        self._LogEvent(
            "Elapsed Time for listRequestionsDeployedStats:" + str(output["elapsed"])
        )

        return output["response"]

    def addRequisition(self, name="selfmonitor"):
        """
        Add Requisition
        """
        self._LogEvent("Running AddRequisition method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/requisitions"
        _data = '{"foreign-source":"' + name + '","node":[]}'
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Content-Type"] = "application/json"
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.post(_url, data=_data, header=_header)
        self._LogEvent("Elapsed Time for addRequisition:" + str(_result.elapsed))

        if _result.status_code != 202:
            self._LogEvent("Failed to add " + name + " requestion")
            raise Exception("Failed to add " + name + " requestion")

    def listRequisitionDefinition(self, name="selfmonitor"):
        """
        List Requisition Definition
        """
        self._LogEvent("Running listRequisitionDefinition method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/foreignSources/" + name
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.get(_url, header=_header)

        if _result.status_code != 200:
            self._LogEvent("Failed to get " + name + " requestion definitions")
            raise Exception("Failed to get " + name + " requestion definitions")

        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        self._LogEvent(
            "Elapsed Time for listRequisitionDefinition:" + str(output["elapsed"])
        )

        return output["response"]

    def clearRequisitionDefinitionDetectors(self, name="selfmonitor"):
        """
        Clears Requisition Definition Detectors
        """
        self._LogEvent("Running clearRequisitionDefinitionDetectors method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/foreignSources"
        _tmp_data = self.listRequisitionDefinition(name)
        _data = _tmp_data
        _data["detectors"] = []
        print()
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Content-Type"] = "application/json"
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Content-Length"] = str(len(_data))
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.post(
            _url, data=json.dumps(_data), header=_header
        )

        self._LogEvent(
            "Elapsed Time for clearRequisitionDefinitionDetectors:"
            + str(_result.elapsed)
        )

        if _result.status_code != 202:
            self._LogEvent("Failed clear " + name + " requestion's detectors")
            raise Exception("Failed clear " + name + " requestion's detectors")

    def clearRequisitionDefinitionPolicies(self, name="selfmonitor"):
        """
        Clears Requisition Definition Policies
        """
        self._LogEvent("Running clearRequisitionDefinitionDetectors method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/foreignSources"
        _tmp_data = self.listRequisitionDefinition(name)
        _data = _tmp_data
        _data["policies"] = []
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Content-Type"] = "application/json"
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.post(
            _url, data=json.dumps(_data), header=_header
        )

        self._LogEvent(
            "Elapsed Time for clearRequisitionDefinitionPolicies:"
            + str(_result.elapsed)
        )
        if _result.status_code != 202:
            self._LogEvent("Failed clear " + name + " requestion's policies")
            raise Exception("Failed clear " + name + " requestion's policies")

    def addRequisitionDefinitionDetector(
        self, name="selfmonitor", detectorname="", classname="", parameters=[]
    ):
        """
        Clears Requisition Definition Policies
        """
        self._LogEvent("Running clearRequisitionDefinitionDetectors method")
        _url = self.SERVER_WEB_URL + "/opennms/rest/foreignSources"
        _tmp_data = self.listRequisitionDefinition(name)
        _data = _tmp_data
        _data["detectors"].append(
            {"name": detectorname, "class": classname, "parameter": parameters}
        )
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Content-Type"] = "application/json"
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"
        _result = self.CONNECTION_WRAPPER.post(
            _url, data=json.dumps(_data), header=_header
        )

        if _result.status_code != 202:
            self._LogEvent("Failed to add " + detectorname + " detector ")
            raise Exception("Failed to add " + detectorname + " detector ")

    def deleteRequisition(self, name="selfmonitor"):
        """
        Deletes a requisition
        """
        self._LogEvent("Running deleteRequisition method")
        _url = self.SERVER_WEB_URL
        _header = {}
        _header["user-agent"] = self.DEFAULT_HEADER["user-agent"]
        _header["Content-Type"] = "application/json"
        _header["Accept"] = "application/json, text/plain, */*"
        _header["Origin"] = self.SERVER_WEB_URL
        _header["Referer"] = (
            self.SERVER_WEB_URL + "/opennms/admin/ng-requisitions/index.jsp"
        )
        _header["DNT"] = "1"

        for path in [
            "/opennms/rest/foreignSources/deployed/" + name,
            "/opennms/rest/foreignSources/" + name,
            "/opennms/rest/requisitions/deployed/" + name,
            "/opennms/rest/requisitions/" + name,
        ]:
            _result = self.CONNECTION_WRAPPER.delete(_url + path, _header)
            self._LogEvent("Elapsed Time for deleteRequisition:" + str(_result.elapsed))
            if _result.status_code != 202:
                self._LogEvent("Failed to delete " + name + " requestion ")
                raise Exception("Failed to delete " + name + " requestion ")

    #                             #
    # --> Events              <-- #
    #                             #
    def get_all_events(self):
        self._LogEvent("Running get_all_events method")
        _url = self.SERVER_WEB_URL+"/opennms/api/v2/events"
        _result = self.CONNECTION_WRAPPER.get(_url,self.DEFAULT_HEADER)
        if _result.status_code != 200:
            self._LogEvent("Failed to get events")
            raise Exception("Failed to get events")
        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        self._LogEvent(
            "Elapsed Time for get_all_events:" + str(output["elapsed"])
        )

        return output["response"]

    def get_events_count(self):
        self._LogEvent("Running get_events_count method")
        _url = self.SERVER_WEB_URL+"/opennms/api/v2/events/count"
        _result = self.CONNECTION_WRAPPER.get(_url,self.DEFAULT_HEADER)
        if _result.status_code != 200:
            self._LogEvent("Failed to get events")
            raise Exception("Failed to get events")
        output = {}
        output["response"] = _result.json()
        output["elapsed"] = _result.elapsed
        self._LogEvent(
            "Elapsed Time for get_events_count:" + str(output["elapsed"])
        )

        return output["response"]
