
import subprocess
import xml.etree.ElementTree as ET
import re,logging,math
from collections import Counter,defaultdict
from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor


class DeviceParser():

    def Parse_storage_xml_from_list(storages):
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
                "Count":0,
                "Serial_Numbers":"",
                "Models":"No Drives Present",
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

    def __init__(self,template):
        self.TEMPLATE = template
        self.logger = logging.getLogger("DeviceParser")
        self.re = ErrorlessRegex()
        self.func_table = {
            "Webcam":self.parse_webcam,
            "Graphics_Controller":self.parse_Graphics_Controller,
            "Optical_Drive":self.parse_Optical_Drive,
            "CPU":self.parse_CPU,
            "Memory":self.parse_Memory,
            "Display":self.parse_Display,
            "Battery":self.parse_Battery,
            "Storage_Data_Collection":self.parse_Storage_information
            
        }
        
    def build_xml_tree(self):
        #tree = ET.ElementTree(self.TEMPLATE)
        #template = tree.getroot()
        root = ET.Element("Devices")
        #for index,child in enumerate(template):
        for index,child in enumerate(self.TEMPLATE):
            if child.tag in self.func_table:
                self.logger.info("function for tag \"{0}\" found".format(child.tag))
                new_children = self.func_table[child.tag]()
                self.logger.info("updating \"{0}\" to new tag(s) \"{1}\"".format(child.tag, [i.text if i.text != None else i for i in new_children]))
                for new_child in new_children:
                    root.append(new_child)
            else:
                self.logger.info("no function for tag \"{0}\" found".format(child.tag))
                
        return root
    
    def parse_Storage_information(self):
        """
        create the storage tags and Storage_Data_Collection tag
        """
        storages = self.parse_storages()
        storage_data_xml = DeviceParser.Parse_storage_xml_from_list(storages)
    
        return [storage_data_xml] + storages      

    def parse_storages(self):
        with open("specs/disks.txt","r") as f:
            data = f.read().split("\n")
            
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
                el = ET.Element(tag)
                el.text = text
                parent.append(el)

            for drive in drives:
                storage_xml = ET.Element("Storage")
                for key,value in drive.items():
                    create_child(key,value,storage_xml)
                storages.append(storage_xml)
            
            self.logger.info("Storage xml list: {0}".format(storages))
            return storages
        
        drives = make_list_of_drives()
        drive_xml_list = make_list_of_storage_xml(drives)
        return drive_xml_list

    def parse_Battery(self):
        battery_xml = ET.Element("Battery")
        health_xml = ET.Element("Health")
        health_xml.text = "Not Present"
        disposition_xml = ET.Element("Disposition")
        disposition_xml.text = "Not Present"
        
        with open("specs/battery.txt","r") as f:
            data = f.read()
            
        capcity = self.re.find(r"capacity:\s*([\d\.]+)%", data)
        if capcity != REGEX_ERROR_MSG:
            #battery detected
            battery_life = round(float(capcity),2)
            health_xml.text = str(battery_life)
            if battery_life > 50:
                disposition_xml.text = "Passed - Included"
            else:
                disposition_xml.text = "Failed - Removed"
        
        battery_xml.append(health_xml);battery_xml.append(disposition_xml)
        return [battery_xml]
           
    def parse_Display(self):
        with open("specs/display.txt","r") as f:
            data = f.read()
        
        display_xml = ET.Element("Display")
        resolution_xml = ET.Element("Resolution")
        resolution_xml.text = "No Integrated display"
        
        size_xml = ET.Element("Size")
        size_xml.text = "No Integrated display"
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
        
        matches = re.search(r"eDP\S*\s+connected\s+(\d+x\d+)[^\n]*?\s(\d+mm x \d+mm)",data)
        if matches != None:
            #Internal display found
            width,height = [int(i) for i in matches.group(1).split("x")]
            gcd = math.gcd(width, height)
            aspect_ratio = f" ({width // gcd}:{height // gcd})"

            resolution_xml.text = matches.group(1) + aspect_ratio
            
            size_xml.text= str(round(hypotenuse_from_string(matches.group(2)))) + "\""
            self.logger.info("eDP found, res: \"{0}\", size: \"{1}\"".format(resolution_xml.text,size_xml.text))
        return [display_xml]
    
    def parse_Memory(self):
        with open("specs/memory.txt","r") as f:
            data = f.read()

        memory_xml = ET.Element("Memory")
        
        def create_child(tag,data):
            xml = ET.Element(tag)
            xml.text = data.strip()
            memory_xml.append(xml)
        
        def search_find_add(regex,name):
            x = self.re.find(regex, data)
            if x != REGEX_ERROR_MSG:
                create_child(name,x)
                return True
            return False
        
        ramSlots = str(len(self.re.find_all(r"\*-bank:\d", data)))
        create_child("Slots",ramSlots)

        

        occupied = str(len(self.re.find_all(r"\*-bank:\d\n(?:.*\n)*?\s+serial:", data)))
        create_child("Occupied_Slots",occupied)
        
        #search_find_add(r""\*-bank:\d\n(?:.*\n)*?\s+clock:(.*?)(?:\n|\()","Speed") ram speed from the clock section
        search_find_add(r"\*-bank:\d\n(?:.*\n)*?\s+description:\s*(?:.*)([0-9]{4} MHz)","Speed") #ram speed from the description
        search_find_add(r"\*-memory\n(?:.*\n)*?\s+size:\s+(\d+\S+)","Size")
        
        if not search_find_add(r"((?:\w*DIMM\s)*\w*DDR\d)","Type"):
            #failed to get type
            speed = int(memory_xml.find("Speed").text.replace(" MHz",""))
            if speed > 4000:
                create_child("Type","DRR5")
            else:
                self.logger.error("ram type detection fall through(s) failed")
                print("failed to detect ram type")
                exit(1)
             
        
        #path GiB to GB
        memory_xml.find("Size").text = memory_xml.find("Size").text.replace("i","")

        self.logger.info("Memory found")
        return [memory_xml]
    
    def parse_CPU(self):
        with open("specs/cpu.txt","r") as f:
            data = f.read()
        
        cpus = []
        cpu_segments = self.re.find_all(r"\*-cpu\n([\s\S]*?)(?=\n\s*\*-cpu|\Z)",data)
        for cpu_data in cpu_segments:
            cpu_xml = ET.Element("CPU")
            
            def search_find_add(regex,name):
                x = self.re.find_first(regex,cpu_data)
                xml = ET.Element(name)
                xml.text=x.strip()
                cpu_xml.append(xml)
            
            #search_find_add([r"(Intel\(R\) (Celeron\(R\)|Core\(TM\) \w+)|AMD Ryzen \d+( PRO)*)"],"Family")
            #search_find_add([r"(Intel\(R\) (?:\w+\(\w{1,2}\))|AMD Ryzen \d+( PRO)*)"],"Family")
            search_find_add([r"((Intel\(R\) (?:Core\(\w{2}\) [Ii]\d|\w+\(\w{1,2}\)))|(AMD Ryzen \d+( PRO)*))"],"Family")
            
            search_find_add([
                r"product:.*\w\) ([^@]*?)(?:CPU)? @",#maybe global intel??
                #r"product:.*(?:(i\d-.*))CPU @",
                #r"product:.*(?:(i\d-.*)(?:CPU)*).*@", #normal intel
                #r"product:.*Celeron\(.\) ([0-9a-zA-Z]+) @", #intel celeron
                r"product: AMD Ryzen \d+(?: PRO)*\s*(.*) w\/", #amd 
            ],"Model")
            search_find_add([
                r"product:.*@ (.*)", #try to extract the clock speed from the product name, works for intel, amd not so much
                r"capacity:(.*)",
                r"size:(.*)"],"Speed")
            search_find_add([r" cores=(\d+) "],"Cores")
        
            self.logger.info("CPU found \"{0}\"".format(cpu_xml))
            cpus.append(cpu_xml)
        
        return cpus
            
    def parse_Optical_Drive(self):
        with open("specs/disks.txt","r") as f:
            data = f.read().split("\n")
        r = ET.Element("Optical_Drive")
        r.text = "Not Present"
        
        def detect_and_eject():
            mount_disk = CommandExecutor.run(["mount /dev/sr0 /mnt/cdrom"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            if mount_disk.returncode == 0 or "no medium" not in mount_disk.stderr.decode("utf-8"):
                CommandExecutor.run(["umount /mnt/cdrom"],stdout=-1,stderr=-1,shell=True)
                CommandExecutor.run(["eject /dev/sr0"],stdout=-1,stderr=-1,shell=True)

        for line in data:
            matches = self.re.find_all(r'"([^"]*)"',line)
            if len(matches)==6 and matches[1] != "" and matches[5] == "1":
                if "DVD" in matches[1] or "R+W" in matches[1]:
                    detect_and_eject()
                    r.text="Present"
        return [r]
    
    def parse_Graphics_Controller(self):
        with open("specs/video.txt","r") as f:
            data = f.read()

        controller_list = []
        graphics_controllers = self.re.find_all(r"\d{2}: PCI([\s\S]+?)(?=\d{2}: PCI|$)",data)

        for controller_text in graphics_controllers:
            driver = self.re.find(r'Driver: "(.*)"',controller_text)
            if "amd" in driver:
                #amd integrated graphics
                with open("specs/cpu.txt","r") as f:
                    cpu = f.read()
                cpu_name = self.re.find(r"product: (.*)",cpu)
                graphics_controller = cpu_name.split("w/")[1].strip()
                
            elif "nvidia" in driver:
                model = self.re.find_first([r"Model:\s*\"(?:.*)\[\s*(.*)\s*\]\""],controller_text)
                graphics_controller = "Nvidia "+model
            else:
                graphics_controller = self.re.find_first([
            r"Model:\s*\"(?:.*)\[\s*(.*)\s*\/(?:.*)\]\"",
            r"Model:\s*\"(?:.*)\[\s*(.*)\s*\]\"",
            r"Model:\s*\"(.*)\"" #fall throughh            
                ],controller_text)
            
            controller_list.append(graphics_controller.strip())
            self.logger.info("Graphics controller found \"{0}\"".format(graphics_controller))
                
        
        
        r = ET.Element("Graphics_Controller")
        
        r.text = ", ".join(controller_list)
        return [r]
    
    def parse_webcam(self):
        with open("specs/webcam.txt","r") as f:
            data = f.read()
        r =ET.Element("Webcam")
        
        if "No such file or directory" in data:
            r.text = "Not present"
        else:
            r.text = "720p HD Webcam"
        return [r]
    

    