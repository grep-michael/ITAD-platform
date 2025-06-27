from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor 
import xml.etree.ElementTree as ET
import re,logging,math,subprocess
from collections import Counter,defaultdict

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

                if drive[0] > 1:
                    i += drive[0]
                i+=1
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
                    
                    matches[4] = matches[4][:-1] +" "+ matches[4][-1:] +"B"
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

        health_xml = self.create_element("Health","Not Present") 
        disposition_xml = self.create_element("Disposition","Not Present")
            
        capcity = self.re.find(r"capacity:\s*([\d\.]+)%", data)
        if capcity != REGEX_ERROR_MSG:
            #battery detected
            battery_life = round(float(capcity),2)
            health_xml.text = str(battery_life) + "%"
            if battery_life > 50:
                disposition_xml.text = "Passed - Included"
            else:
                disposition_xml.text = "Failed - Below Minimum Threshold"
        
        current_wattage = self.re.find(r"energy:\s*(\d{1,2}.*\d*) Wh",data)
        try:
            if float(current_wattage) < 1:
                disposition_xml.text = "Failed - No Power Output"
        except:
            pass
        
        battery_xml.append(health_xml);battery_xml.append(disposition_xml)
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

        memory_xml = self.create_element("Memory")
        
        def create_child(tag,data):
            xml = self.create_element(tag,data.strip())
            memory_xml.append(xml)
        
        def search_find_add(regex,name):
            x = self.re.find(regex, data)
            if x != REGEX_ERROR_MSG:
                create_child(name,x)
                return True
            return False
        
        ramSlots = str(len(self.re.find_all(r"\*-bank:\d", data)))
        create_child("Slots",ramSlots)

        #if the bank has a serial then its occupied
        occupied = str(len(self.re.find_all(r"\*-bank:\d\n(?:.*\n)*?\s+serial:", data)))
        create_child("Occupied_Slots",occupied)
        
        #search_find_add(r""\*-bank:\d\n(?:.*\n)*?\s+clock:(.*?)(?:\n|\()","Speed") ram speed from the clock section
        search_find_add(r"\*-bank:\d\n(?:.*\n)*?\s+description:\s*(?:.*)([0-9]{4} MHz)","Speed") #ram speed from the description
        search_find_add(r"\*-memory\n(?:.*\n)*?\s+size:\s+(\d+\S+)","Size")
        
        if not search_find_add(r"((?:\w*DIMM\s)*\w*DDR\d)","Type"):
            #failed to get type
            self.logger.error("Failed to get memory type")
            speed = int(memory_xml.find("Speed").text.replace(" MHz","").strip())
            self.logger.info("Determining type from speed: {}".format(speed))
            if speed > 4000:
                create_child("Type","DRR5")
            else:
                self.logger.error("ram type detection fall through(s) failed")
                print("failed to detect ram type")
                exit(1)
             
        memory_size_txt = memory_xml.find("Size").text
        #path GiB to GB
        memory_size_txt = memory_size_txt.replace("i","")
        #add space before GB
        _size = re.search(r"(\D+)",memory_size_txt).group(1)
        insert_loc = memory_size_txt.find(_size)
        memory_size_txt = memory_size_txt[:insert_loc] + " " + memory_size_txt[insert_loc:]

        memory_xml.find("Size").text = memory_size_txt

        self.logger.info("Memory found")
        return [memory_xml]

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
                r"((Intel\(R\) (?:Core\(\w{2}\) [Ii]\d|\w+\(\w{1,2}\)))|(AMD Ryzen \d+( PRO)*))",
                r"(AMD PRO \w\d{0,2})",
                ],"Family")
            
            search_find_add([
                r"product:.*Intel\(\w\) Core\(\w{1,2}\) (.*) CPU", #intel core <model> CPU @ speed ...
                r"product:.*Gen Intel\(\w\) Core\(\w{1,2}\) ([^@\n]*)", #11th gen with their fucked up retarded naming convention
                r"product:.*Intel\(\w\) Core\(\w{1,2}\) (Ultra .*)", #"ultras" whatever that fucking means, fuck intel
                r"product:.*Intel\(\w\) Celeron\(\w{1,2}\) (?:CPU)? ([^@]*)", #celeron
                r"product:.*Intel\(\w\) Xeon\(\w{1,2}\) CPU ([^@]*)",
                r"product: AMD Ryzen \d+(?: PRO)*\s*(.*) (?:w\/|with)", #amd ryzen
                r"product: (AMD PRO.*),", #AMD Pros
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
            if len(matches)==6 and matches[1] != "" and matches[5] == "1":
                if "DVD" in matches[1] or "R+W" in matches[1]:
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
            r"Model:\s*\"(.*)\""           
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
                model = self.re.find_first([r"Model:\s*\"(?:.*)\[\s*(.*)\s*\]\""],controller_text)
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