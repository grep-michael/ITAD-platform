from Services.DataRefiner import *
import logging
from Razor.RazorClient import RazorClient

class Finisher():
    
    def finialize_process(root,client,customer:str):
        PatchCPUSerials(root,client,customer)
        LogRefiner.Refine_data()
        XMLTreeRefiner.Refine_tree(root)
        


def PatchCPUSerials(root:ET.Element, client:RazorClient,customer:str):
    
    def setSerial(el:ET.Element, text:str):
        serial = el.find(".//Serial")
        if serial != None:
            serial.text = text

    cpus = root.findall(".//CPU")
    for cpu in cpus:
        uid,err =client.Assets.Get().New_UID(customer)
        if err == None:
            setSerial(cpu,uid)
        else:
            logging.error(f"Failed to get uid for cpu: \n\t{err}\n")
