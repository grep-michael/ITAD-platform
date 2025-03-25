import subprocess,time
import logging,os
from Utils.Utils import CommandExecutor



class NetworkConfig():
    SSID = os.environ["WIFI_SSID"]
    WIFI_PASSWORD=os.environ["WIFI_PASSWORD"]

class NetworkManager():

    def __init__(self):
        self.logger = logging.getLogger("NetworkManager")

    def connect(self) -> bool:
        #network_interfaces = self.parse_nmcli_output() #legacy functions
        #self.connect_interfaces(network_interfaces)
        wifi_connected = self.try_wifi_connect()
        if not wifi_connected[0]:
            print(wifi_connected[1])
        
        internet =  self.can_ping_google()
        if internet:
            self.logger.info("Connect finished successfully")
            return internet
        self.logger.error("Failed to ping google exiting")

        print("Failed to connect to network on any interface, check log")
        exit()

    def try_wifi_connect(self) -> tuple[bool, str]:
        #   nmcli error codes
        #     - 0 Success - indicates the operation succeeded
        #     - 1 Unknown or unspecified error
        #     - 2 Invalid user input, wrong nmcli invocation
        #     - 3 Timeout expired (see --wait option)
        #     - 4 Connection activation failed
        #     - 5 Connection deactivation failed
        #     - 6 Disconnecting device failed
        #     - 7 Connection deletion failed
        #     - 8 NetworkManager is not running
        #     - 9 nmcli and NetworkManager versions mismatch
        #     - 10 Connection, device, or access point does not exist.

        wifi_connect = CommandExecutor.run(["nmcli", "device", "wifi", "connect", NetworkConfig.SSID, "password", NetworkConfig.WIFI_PASSWORD], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if wifi_connect.returncode != 0:
            self.logger.warning("nmcli wifi connected failed with error code {0}".format(wifi_connect.returncode))

            #if "No Wi-Fi device found" in wifi_connect.stderr.decode():
            if wifi_connect.returncode == 1:
                self.logger.error("No wifi devices found")
                return (False,"No wifi devices, ensure ethernet cable is connected")
            
            #if "No network with SSID" in wifi_connect.stderr.decode():
            if wifi_connect.returncode == 10: 
                self.logger.error("No network with ssid {0}".format(NetworkConfig.SSID))
                start = time.time()
                print("No network with name {0} found, retrying for 60s".format(NetworkConfig.SSID))
                while 1:
                    self.logger.warning("network {0} not found ... retrying in 5".format(NetworkConfig.SSID))
                    time.sleep(5)
                    wifi_connect = CommandExecutor.run(["nmcli", "device", "wifi", "connect", NetworkConfig.SSID, "password", NetworkConfig.WIFI_PASSWORD],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    if not "No network with SSID" in wifi_connect.stderr.decode():
                        return (True,None)
                    if time.time() - start > 60:
                        return (False,"Failed to find wifi network with name {0}".format(NetworkConfig.SSID))
                    
            print("error code for nmcli not handled")
            self.logger.error("error code for nmcli not handled in function try_wifi_connect")
            exit(1)
        return (True,None)
        
    def connect_interfaces(self, network_interfaces:list):
        if not self.can_ping_google():
            self.logger.info("no network connection")
            for interface in network_interfaces:
                if interface["TYPE"] == "wifi" and "connected" not in interface["CONNECTION"]:
                    self.logger.info("Attemping wifi connection on " + interface["DEVICE"])
                    CommandExecutor.run(["nmcli", "device", "wifi", "connect", NetworkConfig.SSID, "password", NetworkConfig.WIFI_PASSWORD], check=True)
                    if self.can_ping_google():
                        return
            self.logger.info("Failed to connect to wifi")
        self.logger.info("already connect to internet, continuing")

    def can_ping_google(self) -> bool:
        print("pinging . . .")
        try:
            ping = CommandExecutor.check_output(["ping","8.8.8.8", "-c","4","-t","10"],text=True)
            
            if "Time to live excessed" in ping:
                self.logger.warning("ping failed")
                return False
            self.logger.info("ping success")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning("ping failed")
            return False

    def parse_nmcli_output(self) -> list:
        try:
            self.logger.info("Getting nmcli output")
            device_list = CommandExecutor.check_output(["nmcli","device"],text=True)
            lines = device_list.strip().split("\n")
            headers = lines[0].split()
            header_positions = [lines[0].index(h) for h in headers] + [None]
            network_interfaces = []
            assert len(header_positions) == 5

            for line in lines[1:]:
                values = [line[header_positions[i]:header_positions[i+1]].strip() for i in range(len(headers))]
                network_interfaces.append(dict(zip(headers,values)))
            self.logger.info("all network interfaces {0}".format(network_interfaces))
            return network_interfaces
        except subprocess.CalledProcessError as e:
            self.logger.error("failed to get network devices: {0}".format(e))
            print(f"failed to get network devices")
            print(e)
            exit()