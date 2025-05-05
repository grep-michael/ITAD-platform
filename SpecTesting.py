"""
Randomly grab 100 or so random xmls and their spec files and test DeviceParser against them and their xmls
"""
import sys
sys.path.insert(0, 'src/')
import xml.etree.ElementTree as ET
import re,logging,math,subprocess,os,pathlib,shutil
from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor 
from Services.Parsing.HardwareTreeBuilder import *

from Services.ShareManager import *

logging.basicConfig(filename='./spectesting.log', level=logging.INFO,filemode="w")


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
        xmls = list(self.local_dir.glob("*.xml"))
        if len(xmls) > 1:
            raise Exception("Multiple xmls detected for {}",format(self.local_dir.as_posix()))
        xml = xmls[0]
        print("Loading xml: {}".format(xmls[0].as_posix()))
        #from_share to denote that this xml/root are from our acutal xmls saved to the share
        self.tree_from_share:ET.ElementTree = ET.parse(xml.as_posix())
        self.root_from_share:ET.Element = self.tree_from_share.getroot()
        
        assert xml.stem == self.root.find(".//SYSTEM_INVENTORY/System_Information/Unique_Identifier").text

    def copy_local(self):
        shutil.copytree(self.remote_dir,self.local_dir,dirs_exist_ok=True)



def download_specs() -> list[AssetReport]:
    assest_reports = (ShareConfig.MOUNT_LOCATION + ShareConfig.SHARE_DIRECTORY).replace("\\","")
    uid_list = os.listdir(assest_reports)
    print("Found {} UIDS".format(len(uid_list)))
    
    print("Cutting list to 3")
    uid_list = uid_list[0:3]
    asset_list = []
    for uid in uid_list:
        local_dir = pathlib.Path("spec_testing/{}".format(uid))
        remote_dir = pathlib.Path("{}/{}".format(assest_reports,uid))
        print("Copying {} -> {}".format((remote_dir.as_posix()),(local_dir.as_posix())))
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

        os.chdir(original_cwd)



PARSERS = []
for subclass in BaseDeviceParser.__subclasses__():
    PARSERS.append(subclass())        

if __name__ == "__main__":
    
    SHARE_MANAGER = ShareManager()
    SHARE_MANAGER.mount_share()
    asset_list = download_specs()
    convert_all_specs(asset_list)
    run_parsers_on_assets(asset_list)
    SHARE_MANAGER.close_share()

