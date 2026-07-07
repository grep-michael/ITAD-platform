from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor
from Utilities.PciBlobParsing import *
import xml.etree.ElementTree as ET
import re,logging,math,subprocess,os
from collections import Counter,defaultdict
from pathlib import Path

class BaseDeviceParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.re = ErrorlessRegex()
    
    def read_spec_file(self, filename):
        with open(f"specs/{filename}", "r") as f:
            return f.read()
    
    def create_element(self, tag, text=None):
        element = ET.Element(tag)
        if text is not None:
            element.text = text
        return element

class StorageAggregator:

    def aggregate_storage_data(storages):
        storage_data_xml = ET.Element("Storage_Data_Collection")
        data_dict = []
        storages.sort(key=lambda x: x.find("Model").text )
        
        for storage in storages:
            def storage_get(tag):
                return storage.find(tag).text 
            data_dict.append({
                "Serial_Number":storage_get("Serial_Number"),
                "Model":storage_get("Model"),
                "Size":storage_get("Size"),
                "Type":storage_get("Type")
            })  


        if len(storages) > 0:
            drives = count_by_key_value(data_dict,"Model")
            data_dict = defaultdict(list) 
            data_dict["Count"]=[str(len(drives))]
            i = 0
            while i < len(drives): 
                drive = drives[i]
                for key,item in drive[1].items():
                    append_string = f" x{str(drive[0])}" if drive[0] > 1 else "" 
                    data_dict[key].append(item+append_string)

                i += drive[0]
                #if drive[0] > 1:
                #    i += drive[0]
                #i+=1
            #patches serial number
            data_dict["Serial_Number"] = [i[1]["Serial_Number"] for i in drives]
            #patch all key names
            rename = {"Count":"Count","Model":"Models","Serial_Number":"Serial_Numbers","Size":"Sizes","Type":"Types"}
            data_dict = {rename.get(k, k): v for k, v in data_dict.items()}
            #patch all lists to strings
            data_dict = { k:", ".join(v) for k, v in data_dict.items() }
        else:
            data_dict = {
                "Count":"0",
                "Serial_Numbers":"",
                "Models":"",
                "Sizes":"",
                "Types":""
            }
        
        def make_child(tag,value):
            e = ET.Element(tag)
            e.text = value
            storage_data_xml.append(e)

        for key,item in data_dict.items():
            make_child(key,item)
       
        return storage_data_xml

class StorageParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("disks.txt").split("\n")
        
        invalid_drive_models = [
            "Multi-Card",
            "SD/MMC"
        ]

        def bytes_to_size(size: str) -> str:
            size_units = [" B"," KB"," MB"," GB"," TB"]
            size_int =int(size) 
            if size_int < 1000000000: #less than a gig we dont care
                return size + size_units[0]
            index = 0
            while size_int > 1000:
                size_int = size_int / 1000 
                index += 1
            size_int = int(size_int)
            return str(size_int) + size_units[index]

        def is_drive_valid(matches):
            #if int(matches[4][0]) <= 0: #if size of drive is zero or smaller its a bad drive ignore it
            #    return False
            if "sr" in matches[0][:2]: #if name starts with sr its a disk drive, ignore it
                return False
            for name in invalid_drive_models:
                if name in matches[1]:
                    return False
            
            return True
        
        def make_list_of_drives():
            headers = ["Name","Model","Serial_Number","Type","Size","Hotplug"]
            drives = []
            for line in data:
                
                matches = self.re.find_all(r'"([^"]*)"',line)
                if len(matches)==6 and matches[2] != "" :#and matches[5] != "1": usb check

                    if  "nvme" in matches[0].lower():
                        matches[3] = "NVME"
                    elif matches[3]=="0":
                        matches[3] = "SSD"
                    else:
                        matches[3] = "HDD"
                    
                    
                    matches[4] = bytes_to_size(matches[4])
                    
                    if is_drive_valid(matches):
                        drives.append(dict(zip(headers,matches)))
                    
            self.logger.info("Drive list built: {0}".format(drives))
            return drives
                
        def make_list_of_storage_xml(drives):
            storages = []
            
            def create_child(tag,text,parent):
                el = self.create_element(tag,text)
                parent.append(el)

            for drive in drives:
                storage_xml = self.create_element("Storage")
                for key,value in drive.items():
                    create_child(key,value,storage_xml)
                create_child("Erasure_Compliance","NIST 800-88 1-Pass",storage_xml)
                create_child("Erasure_Results","Failed",storage_xml)
                storages.append(storage_xml)
            
            self.logger.info("Storage xml list: {0}".format(storages))
            return storages
        
        drives = make_list_of_drives()
        drive_xml_list = make_list_of_storage_xml(drives)
        return drive_xml_list

class BatteryParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("battery.txt")

        battery_xml = self.create_element("Battery")

        percentage_xml = self.create_element("Percentage","Not Present") 
        disposition_xml = self.create_element("Disposition","Not Present")
        cycle_count_xml = self.create_element("CycleCount","Not Present")

        capcity = self.re.find(r"capacity:\s*([\d\.]+)%", data)
        if capcity != REGEX_ERROR_MSG:
            #battery detected
            battery_life = round(float(capcity),2)
            percentage_xml.text = str(battery_life) + "%"
            if battery_life > 50:
                disposition_xml.text = "Passed - Included"
            else:
                disposition_xml.text = "Failed - Below Minimum Threshold"
        
        cycles = self.re.find(r"charge-cycles:\s*(\d+)", data)
        if cycles == REGEX_ERROR_MSG:
            cycles = ""
        cycle_count_xml.text = cycles
        
        #current_wattage = self.re.find(r"energy:\s*(\d{1,2}.*\d*) Wh",data)
        #try:
        #    if float(current_wattage) <= 0:
        #        disposition_xml.text = "Failed - No Power Output"
        #except:
        #    pass
        
        battery_xml.append(percentage_xml);battery_xml.append(disposition_xml);battery_xml.append(cycle_count_xml)
        return [battery_xml]

class DisplayParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("display.txt")

        display_xml = self.create_element("Display")

        resolution_xml = self.create_element("Resolution","No Integrated display")
        size_xml = self.create_element("Size","No Integrated display")

        display_xml.append(resolution_xml);display_xml.append(size_xml)
            
        def hypotenuse_from_string(dimensions):
            # Extract numbers from the format "530mm x 300mm"
            match = re.match(r"(\d+)mm x (\d+)mm", dimensions)
            if not match:
                raise ValueError("Invalid format. Expected format: '530mm x 300mm'")
            
            # Convert extracted values to integers
            a_mm, b_mm = map(int, match.groups())

            # Convert mm to inches
            mm_to_inches = 1 / 25.4  # 1 inch = 25.4 mm
            a_in = a_mm * mm_to_inches
            b_in = b_mm * mm_to_inches

            # Calculate the hypotenuse
            hypotenuse_in = math.sqrt(a_in**2 + b_in**2)
            return hypotenuse_in
        
        #matches = re.search(r"\S*\s+connected\s+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",data)
        resolution = self.re.find_first([
            r"\S+\s+connected.*?\n\s+(\d+x\d+)",
            r"\S*\s+connected\s+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",
            r"\S*\s+connected[a-zA-Z\s]+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",
        ],data,1)
        dimensions = self.re.find_first([
            r"\S*\s+connected\s+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",
            r"\S*\s+connected[a-zA-Z\s]+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",
        ],data,2)


        if resolution != REGEX_ERROR_MSG:
            #Internal display found
            resolution_xml.text = resolution
            size_xml.text = str(round(hypotenuse_from_string(dimensions))) + "\""
            self.logger.info("eDP found, res: \"{0}\", size: \"{1}\"".format(resolution_xml.text,size_xml.text))
        
        return [display_xml]

class MemoryParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("memory.txt")
        memorySegments =  self.re.find_all(r"Memory Device\n([\s\S]*?)(?=\n\s*Handle|$)",data)
        returnList = []
        memory_xml = self.create_element("Memory")
        returnList.append(memory_xml)
        def create_child(tag,data):
            xml = self.create_element(tag,data.strip())
            memory_xml.append(xml)
        UNITS = {
            "B":  1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        def parse_size(size_str: str) -> int:
            """'15 GB' -> 16106127360"""
            match = re.match(r'([\d.]+)\s*([A-Za-z]+)', size_str.strip())
            if not match:
                return 0#ValueError(f"Unrecognized size format: {size_str!r}")
            value, unit = float(match.group(1)), match.group(2).upper()
            if unit not in UNITS:
                return 0
            return int(value * UNITS[unit])

        def format_size(num_bytes: int) -> str:
            """16106127360 -> '15.0 GB'"""
            for unit in reversed(list(UNITS)):
                if num_bytes >= UNITS[unit]:
                    return f"{num_bytes / UNITS[unit]:.4g} {unit}"
            return f"{num_bytes} B"

        create_child("Slots",str(len(memorySegments)))
        highestSpeed = 0
        totalCapacity = 0
        occupiedSlots = 0
        ramType = ""

        for segment in memorySegments:
            width = self.re.find(r"^\s*Speed:\s*(.+)$",segment,re.MULTILINE)
            if width == "Unknown" or width == REGEX_ERROR_MSG:
                continue
            deviceXml = self.create_element("Memory_Device")
            occupiedSlots += 1

            speed = int(self.re.find(r"^\s*Speed:\s*(.+)$",segment,re.MULTILINE))
            if speed > highestSpeed:
                highestSpeed = speed
            size = parse_size(self.re.find(r"^\s*Size:\s*(.*)$",segment,re.MULTILINE))
            totalCapacity += size

            deviceXml.append(
                self.create_element("Size",format_size(size))
            )
            deviceXml.append(
                self.create_element("Speed",f"{highestSpeed} MHz")
            )
            deviceXml.append(
                self.create_element("Serial_Number",self.re.find(r"^\s*Serial Number: (.*)$",segment,re.MULTILINE))
            )
            ramType = self.re.find(r"^\s*Type: (.*)$",segment,re.MULTILINE)
            deviceXml.append(
                self.create_element("Type",ramType)
            )
            returnList.append(deviceXml)

        create_child("Occupied_Slots",str(occupiedSlots))
        create_child("Size",format_size(totalCapacity))
        create_child("Type",ramType)
        create_child("Speed",f"{highestSpeed} MHz")

        self.logger.info("Memory found")
        return returnList

class CPUParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("cpu.txt")
        cpus = []
        #cpu_segments = self.re.find_all(r"\*-cpu\n([\s\S]*?)(?=\n\s*\*-cpu|\Z)",data)
        cpu_segments = self.re.find_all(r"\*-cpu:*\d*\n([\s\S]*?)(?=\n\s*\*-cpu|\Z)",data)

        for cpu_data in cpu_segments:
            cpu_xml = self.create_element("CPU")
            
            def search_find_add(regex,name):
                x = self.re.find_first(regex,cpu_data)
                xml = self.create_element(name,x.strip())
                cpu_xml.append(xml)
            
            #search_find_add([r"(Intel\(R\) (Celeron\(R\)|Core\(TM\) \w+)|AMD Ryzen \d+( PRO)*)"],"Family")
            #search_find_add([r"(Intel\(R\) (?:\w+\(\w{1,2}\))|AMD Ryzen \d+( PRO)*)"],"Family")
            search_find_add([
                r"((Intel\(.+\) (?:Core\(\w{2}\) [Ii]\d|\w+\(\w{1,2}\)))|(AMD Ryzen \d+( PRO)*))",
                r"(AMD PRO \w\d{0,2})",
                r"(AMD EPYC)"
                ],"Family")
            
            search_find_add([
                r"product:.*Intel\(\w\) Core\(\w{1,2}\) (.*) CPU", #intel core <model> CPU @ speed ...
                r"product:.*Gen Intel\(\w\) Core\(\w{1,2}\) ([^@\n]*)", #11th gen with their fucked up naming convention
                r"product:.*Intel\(\w\) Core\(\w{1,2}\) (Ultra .*)", #ultras
                r"product:\s*Intel\([^)]*\)\s*Celeron\([^)]*\)\s*(?:CPU\s+)?([A-Z0-9]+)(?:\s+CPU)?", #celeron
                r"product:.*Intel\(\w\) Xeon\(\w{1,2}\)\s+CPU ([^@]*)",
                r"product:.*Intel\(\w\) Xeon\(\w{1,2}\)\s+(.*)\s+CPU",
                r"product: AMD Ryzen \d+(?: PRO)*\s*(.*) (?:w\/|with)", #amd ryzen
                r"product: AMD (.*)\s*(?:w\/|with)",
                r"product: (AMD PRO.*)", #AMD Pros
                r"product: (AMD EPYC \d+) \d+-Core Processor"

            ],"Model")
            
            search_find_add([
                r"product:.*@ (.*)", #try to extract the clock speed from the product name, works for intel, amd not so much
                r"capacity:(.*)",
                r"size:(.*)"],"Speed")
            search_find_add([r" cores=(\d+) "],"Cores")
            def patch_speed():
                speed = cpu_xml.find("Speed").text
                if "MHz" in speed:
                    a = speed.split("MHz")
                    if len(a[0]) < 4: return
                    spd = a[0][0] + "." +a[0][1:3] + "GHz"
                    cpu_xml.find("Speed").text = spd
                
            patch_speed()
            self.logger.info("CPU found \"{0}\"".format(cpu_xml))
            cpus.append(cpu_xml)
        #patch cpu cpu counts in    
        cpu_count = len(cpus)
        for i in cpus:
            cnt = ET.Element("Count")
            cnt.text = str(cpu_count)
            i.append(cnt)
        
        return cpus

class OpticalDriveParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("disks.txt").split("\n")
        r = self.create_element("Optical_Drive","Not Present")

        for line in data:
            matches = self.re.find_all(r'"([^"]*)"',line)
            if "sr0" in  matches[0]:
                self.detect_and_eject()
                r.text="Present"
        return [r]

    def detect_and_eject(self):
        #sr0 should be the default for any disk drive unless theres multiple disk drives
        mount_disk = CommandExecutor.run(["mount /dev/sr0 /mnt/cdrom"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        if mount_disk.returncode == 0 or "no medium" not in mount_disk.stderr.decode("utf-8"):
            CommandExecutor.run(["umount /mnt/cdrom"],stdout=-1,stderr=-1,shell=True)
            CommandExecutor.run(["eject /dev/sr0"],stdout=-1,stderr=-1,shell=True)

class GraphicsControllerParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("video.txt")
        controller_list = []
        graphics_controllers = self.re.find_all(r"\d{2}: PCI([\s\S]+?)(?=\d{2}: PCI|$)",data)

        for controller_text in graphics_controllers:
            #defaults, we will override if we can
            graphics_controller = self.re.find_first([
            r" Device:.*\[(.*)\]",
            r" Device:.*\"(.*)\"",
            r"Model:\s*\"(?:.*)\[\s*(.*)\s*\/(?:.*)\]\"",
            r"Model:\s*\"(?:.*)\[\s*(.*)\s*\]\"",
            r"Model:\s*\"(.*)\"",
                ],controller_text)
            

            driver = self.re.find(r'Driver: "(.*)"',controller_text)
            if "amd" in driver:
                self.logger.info("AMD graphics found")
                #amd integrated graphics
                try:
                    with open("specs/cpu.txt","r") as f:
                        cpu = f.read()
                    cpu_name = self.re.find(r"product: (.*)",cpu)
                    graphics_controller = cpu_name.split("w/")[1].strip()
                except:
                    self.logger.error("Faild to get Graphics controller from the cpu section")
                    pass
                
            elif "nvidia" in driver:
                self.logger.info("Nividia Graphics detected")
                model = self.re.find_first([
                    r"Model:\s*\"(?:.*)\[\s*(.*)\s*\]\"",
                    r"Model:\s*\"(?:.*)\[\s*(.*)\s*\/(?:.*)\]\"",
                    r"Model:\s*\"(.*)\"",
                    ],controller_text)
                graphics_controller = "Nvidia "+model
            
            
            controller_list.append(graphics_controller.strip())
            self.logger.info("Graphics controller found \"{0}\"".format(graphics_controller))
                
        r = self.create_element("Graphics_Controller",", ".join(controller_list))
        return [r]

class WebcamParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("webcam.txt")
        r = self.create_element("Webcam")
        
        if "No such file or directory" in data:
            r.text = "Not present"
        else:
            r.text = "720p HD Webcam"
        return [r]

class PowerSupplyParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("smbios.txt")
        powersupplies = []
        ps_segments = self.re.find_all(r"System Power Supply\n([\s\S]*?)(?=\n\s*Hot Replaceable)",data)
        
        psCollection = self.create_element("Power_Supply_Data_Collection")
        psCollection.append(self.create_element("Count",str(len(ps_segments))))
        
        models = [self.re.find_first([r"Model Part Number: (.*)"],ps) for ps in ps_segments]
        psCollection.append(self.create_element("Models",",".join(models)))
        
        powersupplies.append(psCollection)

        for ps in ps_segments:
            ps_xml = self.create_element("Power_Supply")
            ps_xml.append(
                self.create_element("Serial_Number",self.re.find(r"Serial Number: (.*)",ps))
            )
            ps_xml.append(
                self.create_element("Model",self.re.find(r"Model Part Number: (.*)",ps))
            )
            ps_xml.append(
                self.create_element("Name",self.re.find(r"Name: (.*)",ps))
            )
            powersupplies.append(ps_xml)

        return powersupplies

class NetworkCardParser(BaseDeviceParser):
    def parse(self):
        
        interfaces = list(Path("/sys/class/net/").glob("enp*"))
        if len(interfaces) <=0:
            return []
        iface = interfaces[0]
        vpdPath = os.path.join(iface,"device","vpd")
        try:
            with open(vpdPath,"rb") as f:
                vpd = parse_vpd(f)
                xml = self.create_element("Network_Card")
                xml.append(
                    self.create_element("Serial",vpd.get("SN","NotFound"))
                )
                xml.append(
                    self.create_element("Model",vpd.get("PN","NotFound"))
                )
                xml.append(
                    self.create_element("Name",vpd.get("Name","NotFound"))
                )
                return [xml]
        except FileNotFoundError:
            return []
        
