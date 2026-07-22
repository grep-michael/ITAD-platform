from Services.DataRefiner import *
import logging
from Razor.RazorClient import RazorClient
from Context import *


class Finisher():
    
    def finialize_process(ctx:Context):#root,client,customer:str):
        PatchCPUSerials(ctx.root,ctx.client,ctx.asset.customer)
        LogRefiner.Refine_data()
        XMLTreeRefiner.Refine_tree(ctx.root)
        


def PatchCPUSerials(root:ET.Element,client:RazorClient,customer:str):
    
    def setSerial(el:ET.Element, text:str):
        serial = el.find(".//Serial")
        if serial != None:
            serial.text = text
        else:
            logging.error(f"Failed to find cpu serial to path")

    cpus = root.findall(".//CPU")
    for cpu in cpus:
        uids,err = client.Assets.Get().New_UID(customer)
        if err == None and len(uids) == 1:
            logging.info(f"Got uid for cpu serial: {uids[0]}")
            setSerial(cpu,uids[0])
        else:
            logging.error(f"Failed to get uid for cpu: \n\t{err}\n")
