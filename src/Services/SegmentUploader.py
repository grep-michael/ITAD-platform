import xml.etree.ElementTree as ET
from Razor.models import *
from Razor.RazorClient import *
import logging,math



# commodity id, xml mapping, weight
CommodityMap = [
    (52,".//Memory_Device",0.1),
    (381,".//CPU",0.31),
    (306,".//Power_Supply",2.2),
    (451,".//Slot_1",0.2),
]


def XMLToAsset(element:ET.Element,):
    def get(tag: str) -> str:
        el = element.find(f".//{tag}")
        return el.text if el is not None else None
    return Asset(
        model=get("Model"),
        serial=get("Serial"),
    )

class SegmentUploader:
    def __init__(self):
        self.client = RazorClient()
        self.logger = logging.getLogger(self.__class__.__name__)
        err = self.client.Login()
        if err != None:
            self.logger.error(err)
            raise Exception(f"Failed to login to razor client: {err}")
    
    def UploadXML(self, root:ET.Element)-> error:
        serial = root.find(".//System_Serial_Number").text
        assets, err = self.client.Assets.Get().By_Serial(serial)
        if err != None or len(assets)<1:
            self.logger.error(err)
            return f"Failed UploadXML error: {err}"
        thisAsset = assets[0]
        
        assetLot, err = self.client.Lots.Post().Get_Lot_Information(thisAsset.lotId)
        if err != None or len(assets)<1:
            self.logger.error(err)
            return f"Failed UploadXML error: {err}"
        lots = [o for o in assetLot.rows]
         
        for item in CommodityMap:

            assets:list[Asset] = [XMLToAsset(el) for el in root.findall(item[1])] 
            commodityLot = next((obj.ItemAutoName for obj in lots if obj.CommodityId == item[0]),None)
            
            if commodityLot == None:
                self.logger.info(f"Making sublot: ")
                self.logger.info(f"{thisAsset.lotId},{item[0]},{thisAsset.customerId},{thisAsset.recyclingOrderId},{thisAsset.customerId},{(len(assets)*item[2])}")
                lot, err = self.client.Lots.Post().Make_Sub_Lot(thisAsset.lotId,item[0],thisAsset.customerId,thisAsset.recyclingOrderId,7766,
                    weight=(len(assets)*item[2])
                )
                if err != None:
                    self.logger.error(err)
                    return err
                commodityLot = lot.Name

            uids, err = self.client.Assets.Get().New_UID(thisAsset.customer,quantity=len(assets))
            if err != None or len(uids)<1:
                self.logger.error(err)
                return err
        
            for index, asset in enumerate(assets):
                asset.lotAutoName = commodityLot
                asset.isUnique = False
                asset.location = "PL 1"
                asset.quantity = 1
                asset.assetWorkflowStep = "Data Collection"
                asset.uniqueId = uids[index]
                asset.weight = item[2]
                
                uid, err = self.client.Assets.Post().New_Asset(asset)
                if err != None:
                    self.logger.error(err)
                    return err
                self.logger.info(f"Made Asset: {uid} with model:\"{asset.model}\" serial:\"{serial}\"")
                print(asset.model,asset.serial,uid)
            



        