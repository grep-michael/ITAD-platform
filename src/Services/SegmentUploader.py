import xml.etree.ElementTree as ET
from Razor.models import *
from Razor.RazorClient import *
import logging,math
from Razor.Commodities import *
from Utilities.discord_noitification import send_discord_webhook



def admin_log(embed:dict):
    send_discord_webhook(
        os.getenv("ADMIN_WEBHOOK"),
        [embed],
    )
    logging.critical(embed)

def XMLToAsset(element:ET.Element,):
    def get(tag: str) -> str:
        el = element.find(f".//{tag}")
        return el.text.strip() if el is not None else None
    return Asset(
        model=get("Model"),
        serial=get("Serial"),
        manufacturer=get("Manufacturer"),
    )

class SegmentUploader:
    def __init__(self):
        self.client = RazorClient()
        self.logger = logging.getLogger(self.__class__.__name__)
        err = self.client.Login()
        if err != None:
            self.logger.error(err)
            raise Exception(f"Failed to login to razor client: {err}")
    
    def GetAsset(self,serial)->Asset:
        assets, err = self.client.Assets.Get().By_Serial(serial)
        if err != None or len(assets)<1:
            self.logger.error(f"Failed Get Asset UID by Serial error: {err}")
            return None
        return assets[0]
    
    def GetLots(self, asset:Asset)->list[SortingItem]:
        assetLot, err = self.client.Lots.Post().Get_Lot_Information(asset.lotId)
        if err != None:
            self.logger.error(f"Failed UploadXML error: {err}")
            return None
        return [lot for lot in assetLot.rows]

    def MakeCommodityLot(self,parentAsset:Asset,assets:list[Asset],commodity:CommodityData)->str:
        self.logger.info(f"Making sublot: LotIDmCommodityID,CustomerID,RecyclingOrderID,totalWeight")
        self.logger.info(
            f"{parentAsset.lotId},{commodity.RazorCommodityID},{parentAsset.customerId},{parentAsset.recyclingOrderId},{(len(assets)*commodity.Weight)}"
            )
        lot, err = self.client.Lots.Post().Make_Sub_Lot(
            parentAsset.lotId,commodity.RazorCommodityID,
            parentAsset.customerId,parentAsset.recyclingOrderId,
            7766,weight=(len(assets)*commodity[2])
        )
        if err != None:
            self.logger.error(err)
            return None
        name = commodity.XMLName.replace(".//","")
        admin_log({
            "title": "Made Lot",
            "description": f"Made {name} Lot with ID: {lot.ID}",
            "color": 0xf5a00c,
            "fields": [
                {
                    "name": "LotID",
                    "value": lot.ID,
                    "inline":True
                },
                {
                    "name": "LotName",
                    "value": lot.Name,
                    "inline":True
                }
            ]
        })
        return lot.Name

    def UploadAsset(self,asset:Asset,commodity:CommodityData)->error:
        
        masterId:int
        masterItems, err = self.client.ItemMaster.Get().By_Name(asset.model)
        if err != None:
            man = Manufacurer()
            manufacturers, err = self.client.Manufacurer.Get().All_By_Name(asset.manufacturer)
            if err != None:
                id, err = self.client.Manufacurer.Post().Make_Manufacturer(f"Auto Generated Manufacturer for Asset: {asset.uniqueId}",asset.manufacturer)
                if err != None:
                    return f"Failed making Manufacturer for {asset.uniqueId}: {err}"
                admin_log({
                    "title": "Made Lot",
                    "description": f"Made {asset.manufacturer} Manufacturer with ID: {id}",
                    "color": 0xf5a00c,
                    "fields": [
                            {
                                "name": "ManufacturorID",
                                "value": id,
                            },
                    ]
                })
                man.id = id
                man.name = asset.manufacturer
            else:
                man = manufacturers[0]
            
            id, err = self.client.ItemMaster.Post().Make_ItemMaster(
                man.name,asset.model,commodity.RazorAttributeID,man.id,commodity.RazorPrimaryCategory
            )
            if err != None:
                return f"Failed to make Master item for {asset.model}: {err}"
            masterId = id
        else:
            masterId = masterItems[0].id
        
        asset.itemMasterId = masterId

        uid, err = self.client.Assets.Post().New_Asset(asset)
        if err != None:
            self.logger.error(err)
            return err
        self.logger.info(f"Made Asset: {uid} with model:\"{asset.model}\" serial:\"{asset.serial}\"")


    def UploadXML(self, root:ET.Element)-> error:
        serial = root.find(".//System_Serial_Number").text
        asset = self.GetAsset(serial)
        if asset == None:
            return f"Failed To Get Asset"

        lots:list[SortingItem] = self.GetLots(asset)
        if lots == None:
            return f"Failed to get lots for asset"
         
        for commodity in CommodityList:
            assets:list[Asset] = [XMLToAsset(el) for el in root.findall(commodity.XMLName)]
            commodityLot = next((obj.ItemAutoName for obj in lots if obj.CommodityId == commodity[0]),None)

            if commodityLot == None:
                name = self.MakeCommodityLot(asset,assets,commodity)
                if name == None:
                    return f"Failed to make Commodity Lot"
                commodityLot = name

            uids, err = self.client.Assets.Get().New_UID(asset.customer,quantity=len(assets))
            if err != None or len(uids)<1:
                self.logger.error(err)
                return err
        
            for index, asset in enumerate(assets):
                asset.lotAutoName = commodityLot
                asset.isUnique = False
                asset.location = "Whitestown, IN"
                asset.quantity = 1
                asset.assetWorkflowStep = "Data Collection"
                asset.uniqueId = uids[index]
                asset.weight = commodity[2]
                
                err = self.UploadAsset(asset,commodity)
                if err != None:
                    return err
                return None
            



        