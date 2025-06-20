"""
Randomly grab 100 or so random xmls and their spec files and test DeviceParser against them and their xmls
"""
import sys,re,logging,math,subprocess,os,pathlib,shutil,argparse,random
sys.path.insert(0, 'src/')

from Utilities.Config import Config,ConfigLoader
ConfigLoader.init_spec_testing()

import xml.etree.ElementTree as ET
from copy import deepcopy
from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor 
from Utilities.Finisher import Finisher
from Services.Parsing.HardwareTreeBuilder import *
from Services.DataRefiner import XMLTreeRefiner
from Services.ShareManager import *
from Services.FTPManager import *

args = Config

logging.basicConfig(filename='./spectesting.log', level=logging.INFO,filemode="w")

valid_uids = []

class AssetReport():
    def __init__(self,remote_dir,local_dir):
        self.remote_dir:pathlib.Path = remote_dir
        self.local_dir:pathlib.Path = local_dir 
        self.uid = self.local_dir.stem
    
    def get_path(self):
        return self.local_dir.as_posix()

    def convert_master_spec(self):
        master_spec = self.local_dir.as_posix() + "/system_specs.txt"
        header_regex = r"(========(.*)========)"
        with open(master_spec,"r") as f:
            data = f.read()
        headers = re.findall(header_regex,data)
        for match in headers:
            header = match[0]
            filename = match[1] 
            start = data.find(header)
            end = data.find("========",start + len(header))
            pathlib.Path(self.local_dir.as_posix() + "/specs").mkdir(exist_ok=True)
            with open(self.local_dir.as_posix() + "/specs/" + filename,"w") as f:
                f.write(data[start+len(header):end])
    
    def load_xml(self):
        #xmls = list(self.local_dir.glob("*.xml"))
        #if len(xmls) > 1:
        #    raise Exception("Multiple xmls detected for {}",format(self.local_dir.as_posix()))
        #xml = xmls[0]
        xml_path = self.get_path() + "/{}.xml".format(self.uid)
        print("Loading xml: {}".format(xml_path))
        #from_share to denote that this xml/root are from our acutal xmls saved to the share
        self.tree_from_share:ET.ElementTree = ET.parse(xml_path)
        self.root_from_share:ET.Element = self.tree_from_share.getroot()
        
    def copy_local(self):
        try:
            shutil.copytree(self.remote_dir,self.local_dir)
            print("Copying {} -> {}".format((self.remote_dir.as_posix()),(self.local_dir.as_posix())))
        except:
            print("{} already Exists, skipping".format(self.local_dir.as_posix()))
            pass

    def verify_tree(self,fresh_tree:ET.Element):
        # expected_tree is the tree from our share
        # fresh_tree is the one we just generated 
        elements_to_check = [ # list of element paths to check for the same value
            "SYSTEM_INVENTORY/System_Information/System_Serial_Number",
            "SYSTEM_INVENTORY/System_Information/System_Model",
            "SYSTEM_INVENTORY/System_Information/System_Manufacturer",
            "SYSTEM_INVENTORY/System_Information/System_Chassis_Type",
            "SYSTEM_INVENTORY/System_Information/OS_Installed",
            "SYSTEM_INVENTORY/System_Information/Erasure_Method",
            "SYSTEM_INVENTORY/Devices/Webcam",
            "SYSTEM_INVENTORY/Devices/Graphics_Controller",
            "SYSTEM_INVENTORY/Devices/Optical_Drive",
            "SYSTEM_INVENTORY/Devices/CPU",
            "SYSTEM_INVENTORY/Devices/Memory",
            "SYSTEM_INVENTORY/Devices/Display",
            "SYSTEM_INVENTORY/Devices/Battery",
            "SYSTEM_INVENTORY/Devices/Storage",
        ]

        def normalize_text(text):
            return (text or '').strip()

        def compare_texts(elem1, elem2):
            if normalize_text(elem1.text) != normalize_text(elem2.text):
                print("{} | {} tag text differing - {}:{}".format(self.uid,elem1.tag,elem1.text,elem2.text))
                return False
            #if len(elem1) != len(elem2):
            #    print("{} | {} tag Size differing - {}:{}".format(self.uid,elem1.tag,len(elem1),len(elem2)))
            #    return False
            for c1, c2 in zip(elem1, elem2):
                if not compare_texts(c1, c2):
                    return False
            return True
        def compare_elements(expected:list[ET.Element],fresh:list[ET.Element]):
            
            for i,expected_element in enumerate(expected):
                if args.element != None and expected_element.tag.lower() != args.element.lower():
                    continue
                fresh_element = fresh[i]
                if normalize_text(expected_element.text) != normalize_text(fresh_element.text):
                    print("{} | {} tag text differing - {}:{}".format(self.uid,expected_element.tag,expected_element.text,fresh_element.text))
                for j,expected_child in enumerate(expected_element):
                    fresh_child = fresh_element.find(expected_child.tag)
                    #print(expected_child,fresh_child)
                    if (fresh_child != None and expected_child != None) and normalize_text(expected_child.text) != normalize_text(fresh_child.text):
                        print("{} | {},{} tag text differing - {}:{}".format(self.uid,expected_element.tag,expected_child.tag,expected_child.text,fresh_child.text))
            
                

        for path in elements_to_check:
            try:
                expected_elements = self.root_from_share.findall(path)
                fresh_elements = fresh_tree.findall(path)
                if len(expected_elements) != len(fresh_elements):
                    raise Exception("Element Count differnce! {}".format(path))
                compare_elements(expected_elements,fresh_elements)
            except Exception as e:
                print("Error for {}: {}".format(self.uid,e))
            
def download_assets(search_pattern) -> list[AssetReport]:
    if search_pattern == None:
        search_pattern="*"

    assest_reports = (ShareConfig.MOUNT_LOCATION).replace("\\","")

    uid_list = [it.stem for it in pathlib.Path(assest_reports).glob(search_pattern)]
    print("Found {} UIDS".format(len(uid_list)))
    
    if args.uid == None and args.filename == None:
        uid_list = random.sample(uid_list, 100)
    if args.filename != None:
        uid_list = [uuid for uuid in uid_list if uuid in valid_uids]

    asset_list = []
    for uid in uid_list:
        local_dir = pathlib.Path("spec_testing/{}".format(uid))
        remote_dir = pathlib.Path("{}/{}".format(assest_reports,uid))
        
        ar = AssetReport(remote_dir,local_dir)
        ar.copy_local()
        asset_list.append(ar)
    return asset_list

def convert_all_specs(asset_list:list[AssetReport]):
    for asset in asset_list:
        asset.load_xml()
        asset.convert_master_spec()

def run_parsers_on_assets(asset_list:list[AssetReport]):

    original_cwd = pathlib.Path.cwd()
    for asset in asset_list:
        os.chdir(asset.get_path())

        root = HardwareTreeBuilder.build_hardware_tree()
        XMLTreeRefiner._refine_tree_no_save(root)

        asset.verify_tree(root)
        
        os.chdir(original_cwd)

        ET.indent(root) #formatting
        xml_tree = ET.ElementTree(root) # make tree
        path = asset.get_path()+"/new.xml"
        xml_tree.write(path,encoding="utf-8") #write tree

def patch_xml(asset_list:list[AssetReport]):
    
    original_cwd = pathlib.Path.cwd()
    for asset in asset_list:
        os.chdir(asset.get_path())

        new_root:ET.Element = HardwareTreeBuilder.build_hardware_tree() #what the current xml spec parsing returns
        
        old_root:ET.Element = deepcopy(asset.root_from_share) #a copy of the original xml
        
        #patch the copy to have new parser text 
        for element in old_root.iter():
            if element.tag == args.element:
                element.text = new_root.find(".//"+element.tag).text

        #copy patched xml to new xml for upload to razor
        erp_copy:ET.Element = deepcopy(old_root)

        for element in erp_copy.iter():
            if element.tag not in ["System_Serial_Number","Unique_Identifier",args.element]:
                element.text = None
        
        def remove_sub_child(element_tag):
            for parent in erp_copy.findall(f".//{element_tag}/.."):
                for element in parent.findall(f".//{element_tag}"):
                    parent.remove(element)
        remove_sub_child("Storage_Data_Collection")
        remove_sub_child("Storage")

        os.chdir(original_cwd)

        ET.indent(old_root) #formatting
        xml_tree = ET.ElementTree(old_root) # make tree
        path = asset.get_path()+"/"+asset.uid+".xml"
        xml_tree.write(path,encoding="utf-8") #write tree

        ET.indent(erp_copy) #formatting
        xml_tree = ET.ElementTree(erp_copy) # make tree
        path = asset.get_path()+"/"+asset.uid+"_erp_safe.xml"
        xml_tree.write(path,encoding="utf-8") #write tree

def upload_assets(assetlist:list[AssetReport]):
    ftp = FTPUploadStrategy()

    for asset in assetlist:
        print(asset.remote_dir)
        print(asset.local_dir)

        SHARE_MANAGER.upload_dir(asset.local_dir,asset.uid)
        ftp = FTPUploadStrategy()
        ftp.upload_file("{}/{}_erp_safe.xml".format(asset.local_dir,asset.uid))


if args.filename != None:#
    with open(args.filename,"r") as f:#
        valid_uids = f.readlines()
        valid_uids = [i.strip() for i in valid_uids]



#find . -maxdepth 2 -type f -exec grep -HE '<System_Model>[0-9]*</System_Model>' {} \;
#a depth of 2 here is needed because we dont wanna search old past xml files, just present current ones
if __name__ == "__main__":
    
    #to mass patch
    #./spectesting -f uids.txt -e <element>

    SHARE_MANAGER = ShareManager()
    SHARE_MANAGER.mount_share()
    asset_list = download_assets(args.uid)
    convert_all_specs(asset_list)
    #run_parsers_on_assets(asset_list)
    patch_xml(asset_list)
    upload_assets(asset_list)
    SHARE_MANAGER.close_share()

