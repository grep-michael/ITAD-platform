from datetime import datetime
import hashlib,json,os,types
from typing import Generator
import time
import Razor.mureq as mureq
from Razor.helpers import *
from http.cookies import SimpleCookie
from collections.abc import MutableSet
from urllib.parse import urlparse,urlencode
from Utilities.Config import Config
from Razor.models import *
from abc import ABC, abstractmethod
import dataclasses
from pprint import pprint

"""
Public token is for the front end ui api
Private Token is for the new backend api razor has started to push out
"""

error = str
AccessToken =  str
AccessResponce = MutableSet[AccessToken, error]
APIResponse = MutableSet[T, error]
CompanyIDResponse = MutableSet[int, error]
Lotid = int
LotName = str

        


class RazorClient:
    def __init__(self,instance:str=None):
        self.pubToken:str = ""
        self.privToken:str = ""
        self.COOKIES:dict = {}
        self._CACHE:dict = {}
        self.instance:str = instance or os.getenv("RAZOR_INSTANCE")
        self.instanceDomain:str = urlparse(self.instance).netloc

        self.Assets:AssetsAPI = AssetsAPI(self)
        self.Commodity:CommodityAPI = CommodityAPI(self)
        self.Lots:LotAPI = LotAPI(self)
        self.Manufacurer:ManufacturerAPI = ManufacturerAPI(self)
        self.Lookup:LookupAPI = LookupAPI(self)
        self.ItemMaster:ItemMasterAPI = ItemMasterAPI(self)

    def Request(self,
                method:str,url:str,
                data:dict=None,
                headers:dict=None,
                cache:bool=False,
                #usePriv:bool=False,
                #usePub:bool=False,
                **kwargs
            ) -> mureq.Response:
        reqHeaders = {"User-Agent":"ITADBot","Origin":f"{self.instanceDomain}","Accept": "application/json, text/plain, */*"}
        
        if url.startswith(os.getenv("RAZOR_API")):
            reqHeaders.update({"Authorization":f"Bearer {self.privToken}"})

        if cache:
            key = hashlib.md5(f"{method}{url}{json.dumps(data, sort_keys=True)}".encode()).hexdigest()
            if key in self._CACHE:
                hit = self._CACHE[key]
                tm:datetime = hit[0]
                if (datetime.now() - tm).total_seconds() < 30:
                    return hit[1]
        
        if headers: reqHeaders.update(headers)
        if self.COOKIES: reqHeaders["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.COOKIES.items())  
        response = mureq.request(method, url, json=data,headers=reqHeaders,timeout=300,**kwargs)
        if cache:
            now = datetime.now()
            self._CACHE[key] = (now,response)
        
        set_cookie = response.headers.get("Set-Cookie")
        if set_cookie:
            cookie = SimpleCookie()
            cookie.load(set_cookie)
            self.COOKIES.update({k: v.value for k, v in cookie.items()})
        if os.getenv("DEBUG"):
            print(method, url)
        return response
    
    def Login(self, user:str = None,passwd:str = None) -> error:
        pubTok, err = self.GetPubToken(
            user or os.getenv("RAZOR_USER"),
            passwd or os.getenv("RAZOR_PASSWD")
        )
        if err != None:
            return err
        self.pubToken = pubTok

        self.PopulateAuthCookie(self.pubToken)
        if self.COOKIES.get(".PRODAUTHCOOKIE") == None:
           return "Failed to set Auth Cookie"
        
        privTok, err = self.GetPrivateToken()
        if err != None:
            return err
        self.privToken = privTok

    def GetCompanyID(self)->CompanyIDResponse:
        response = self.Request("GET",f"{self.instance}/api/v1/company-domain/{self.instanceDomain}/to-company",cache=True)
        if response.status_code != 200:
            return (None, f"Error getting CompanyID {response.status_code}-{str(response.body)}")

        id = response.json().get("companyId") 
        return (int(id),None)

    def GetPubToken(self,user:str,passwd:str)-> AccessResponce: 
        copmanyId,err = self.GetCompanyID()
        if err != None:
            return (None,err)
        
        response = self.Request(
                "POST",f"{self.instance}/api/v1/Auth",
                {"login": user, "password": passwd, "companyId": copmanyId},
                {"Content-Type": "application/json", "Referer": f"{self.instance}/v2/account/login"},
                cache=True
            )
        if response.status_code != 200:
            return ("",f"Status Invaild: {response.status_code}")
        return FieldFromJsonResponse("accessToken",response)
    
    def GetPrivateToken(self) -> AccessResponce:
        if self.COOKIES.get(".PRODAUTHCOOKIE") == None:
            return (None,"Auth Cookie Not set")
        response = self.Request("POST",f"{self.instance}/Services/RazorApiProxyService.asmx/GetToken",
                        headers={
                                "Referer":f"{self.instance}/Admin/UserProfile.aspx",
                                "Content-Type": "application/json"
                            }
                        )
        if response.status_code != 200:
            return ("",f"Failed to get Private Token: {response.status_code}")
        try:
            token = response.json().get("d").get("Result").get("Item").get("AccessToken")
            return (token, None)
        except Exception as e:
            return (None, e)
    
    def PopulateAuthCookie(self,token:AccessToken)-> error:
        response = self.Request("POST",f"{self.instance}/api/v1/Redirection/to/",
                    {"url": "/Admin/LotSort.aspx"},
                    {"Content-Type": "application/json", "Authorization": f"Bearer {token}","Referer": f"{self.instance}/api/v1/Redirection/to/"}
                )
        if response.status_code != 200:
            return f"Failed requesting redirect: {response.status_code}"
        
        redirectUrl, err = FieldFromJsonResponse("redirectUrl",response)
        if err != None:
            return err
        response = self.Request("GET",f"{self.instance}{redirectUrl}")
        if response.status_code != 200:
            return f"Failed following Redirect: {response.status_code}"
        return None
    
class RazorClientDependant:
    def __init__(self,client:RazorClient):
        self.api_url = os.getenv("RAZOR_API")
        self._client:RazorClient = client
    
    def error(self, response)-> str:
        return f"{self.__class__.__qualname__} New_Asset error: status-{response.status_code}, Body: {response.body}"

PaginatedResponse = MutableSet[PaginatedList, error]
def PaginateApi(fetch: Callable[[dict],PaginatedResponse], params:dict,**reqArgs) -> Generator[list, None, None]:
    offset = 0
    while True:
        params["offset"] = offset
        response, err = fetch(params,**reqArgs)
        if err != None:
            yield None,err
        else:
            yield response.items, None
        offset += params.get("limit",25)
        if offset >= response.total_records or len(response.items) == 0:
            break

class BaseGetQuery(RazorClientDependant):
    api_path: str
    item_class: type
    
    def __init__(self, client):
        self._api = os.getenv("RAZOR_API")
        super().__init__(client)
    
    def _build_url(self,path:str)->str:
        return f"{self._api}{self.api_path}{path}"

    def _fetch_one(self,path:str,label:str,**reqArgs)->T:
        response = self._client.Request("GET",self._build_url(path),**reqArgs)
        if response.status_code != 200:
            return None, self.error(response)
        return build_dataclass(self.item_class, response.json()), None
    
    def _fetch_many(self,path:str,label:str,**reqArgs)->MutableSet[list[T],error]:
        response = self._client.Request("GET",self._build_url(path),**reqArgs)
        if response.status_code != 200:
            return None, self.error(response)
        return [ build_dataclass(self.item_class, item) for item in response.json() ], None
    
    def List(self, params:dict={"limit":25,"offset":0},**regArgs)->PaginatedResponse:
        response = self._client.Request("GET",self._build_url(f"/all?{urlencode(params)}"),regArgs)

        if response.status_code != 200:
            return None, self.error(response)
        return (
            PaginatedList.from_dict(response.json(), item_mapper=lambda d: build_dataclass(self.item_class, d)),
            None
        )
    
    def All(self, page_limit: int = 25) -> MutableSet[list, error]:
        items, errs = [], []
        for page, err in PaginateApi(self.List, {"offset":0,"limit":page_limit}):
            if err:
                errs.append(err)
            else:
                items.extend(page)
        if errs:
            return items, f"{self.__class__.__qualname__} All error: {errs}"
        return items, None

"""
ASSETS
For some dumb fuck reason, get by uid returns 1 element but get by serial number returns a list.
Even though razor will only let you have 1 asset by serial number
"""

class AssetGetQuery(BaseGetQuery):
    api_path = "/api/v1/Asset"
    item_class = Asset

    def By_UID(self, uid: str) -> MutableSet[list[Asset], error]:
        return self._fetch_one(f"/by-uid/{uid}", f"{self.__class__.__qualname__} By_UID")

    def By_Serial(self, serial: str) -> MutableSet[list[Asset], error]:
        return self._fetch_many(f"/by-serial-number/{serial}", f"{self.__class__.__qualname__} By_Serial")

    def New_UID(self,customerName:str,quantity:int=1) -> MutableSet[list[str],error]:
        base = os.getenv("RAZOR_INSTANCE")
        response = self._client.Request("POST",f"{base}/Services/InventoryRecieveService.asmx/GenerateInventorySerialsOrUIds",
                                data={"customerName":customerName,"mustSave": False, "qty":	quantity},
                            )
        if response.status_code != 200:
            return None, self.error(response)
        js = response.json()
        items:list = js.get("d",{}).get("Item",[])
        return items, None

    def All(self, page_limit: int = 5000):
        return super().All(page_limit)

class AssetPostQuery(RazorClientDependant):

    def __init__(self, client):
        super().__init__(client)

    def New_Asset(self, asset:Asset) -> MutableSet[str,error]:
        data = dataclasses.asdict(asset)
        base = os.getenv("RAZOR_API")
        response = self._client.Request("POST",f"{base}/api/v1/Asset",data=data)
        
        if response.status_code != 201 :
            return None, f"{self.__class__.__qualname__} New_Asset error: status-{response.status_code}, Body: {response.body}"
        data = response.json()
        return data.get("uniqueId"),None

class AssetsAPI(RazorClientDependant):
    def __init__(self, client:RazorClient):
        self._get = AssetGetQuery(client)
        self._post = AssetPostQuery(client)
        super().__init__(client)

    def Get(self) -> AssetGetQuery:
        return self._get

    def Post(self)->AssetPostQuery:
        return self._post

"""
COMMODITIES
"""

class CommodityGetQuery(BaseGetQuery):
    api_path = "/api/v1/Commodity"
    item_class = Commodity

    def By_ID(self, id: int):
        return self._fetch_one(f"/{id}", f"{self.__class__.__qualname__} By_ID")

    def By_Name(self, name: str) -> MutableSet[list[Commodity], error]:
        all_items, err = self.All()
        if err:
            return None, err
        results = []
        for cmd in all_items:
            if name.lower() in cmd.name.lower():
                commodity, err = self.By_ID(cmd.id)
                if err:
                    continue

                if name.lower() == cmd.name.lower():
                    return [commodity]
                else:
                    results.append(commodity)
            
        return results

    def All(self, page_limit: int = 200):
        return super().All(page_limit)

class CommodityAPI(RazorClientDependant):
    def __init__(self, client:RazorClient):
        self.getquery = CommodityGetQuery(client)
        super().__init__(client)

    def Get(self)->CommodityGetQuery:
        return self.getquery
    
"""
LOTS
"""

class MadeLot:
    def __init__(self,id, name):
        self.ID = id
        self.Name = name

class LotPostQuery(RazorClientDependant):
    def __init__(self, client):
        super().__init__(client)

    def Get_Lot_Information(self,lotId:int)-> MutableSet[SortingItemsResponse,error]:
        payload = {
            "request":{
                "_search":False,
                "Data":[lotId],
                "page":1,
                "rows":10000,
                "sidx":"RecyclingOrderItemId",
                "sord":"desc",
            }
        }  
        base = os.getenv("RAZOR_INSTANCE")
        response = self._client.Request("POST",
                                f"{base}/Services/RecyclingOrderItemsService.asmx/SortingItemsLoad",
                                data=payload,
                                headers={
                                        "Content-Type":"application/json",
                                    }
                            )
        if response.status_code != 200:
            return None, self.error(response)
        
        inner = response.json().get("d",{})
        return SortingItemsResponse(
            rows=[build_dataclass(SortingItem, r) for r in inner.get("rows", [])],
            **{k: v for k, v in inner.items() if k != "rows"}
        ),None
        
    def Get_Lot_Parent_key(self,parentId:int)->set[str,error]:
        info, err = self.Get_Lot_Information(parentId)
        if err != None:
            return None, err
        for lot in info.rows:
            if lot.RecyclingOrderItemId == parentId:
                return lot.ParentsKey,None
        return None, f"Failed to get parent key for {parentId}"

    def Make_Sub_Lot(self, 
                        parentLotID:int,CommodityID:int,cusomterID:int,recyclingOrderID:int,locationId:int,
                        weight:int = 1,
                    )->MutableSet[MadeLot,error]:
        
        parentKey, err = self.Get_Lot_Parent_key(parentLotID)
        if err != None:
            return None, f"Failed to get ParentKey: {err}"
        
        payload = {
            "data":{
                "BusinessUnitId":"1",
                "ItemCount":"1",
                "ItemTypeId":CommodityID,
                "LocationId":str(locationId),
                "Net":1,
                "Notes":"",
                "PackagingTypeId":"20",
                "ParentId":str(parentLotID),
                "ParentsKey":parentKey,
                "RecyclingOrderItemId":	-1,
                "Reference":"",
                "StateProgramId":None,
                "Tare":	"0",
                "Weight":str(weight),
                "WorkflowTypeId":"39",
            },
            "recyclingOrderId":str(recyclingOrderID),
            "model":{
                "CustomerId":cusomterID,
                "RecyclingMasterId":CommodityID,
                "RecyclingOrderId":str(recyclingOrderID),
                "RecyclingOrderItemId":str(parentLotID),
                "TagIds":[],
            },
            
        }
        base = os.getenv("RAZOR_INSTANCE")
        response = self._client.Request("POST",
                                        f"{base}/Services/RecyclingOrderItemsService.asmx/SortLot",
                                        data=payload,
                                        headers={
                                            "Referer": f"{base}/Admin/LotSort.aspx?lotIds=%5B{parentLotID}%5D",
                                            "Content-Type":"application/json",
                                            }
                                        )
        if response.status_code != 200:
            return None,self.error(response)
        subLot = response.json().get("d").get("Item")
        return MadeLot(subLot["value"],subLot["label"]),None

class LotAPI(RazorClientDependant):
    def __init__(self, client):
        self._post = LotPostQuery(client)

        super().__init__(client)
    
    def Post(self)->LotPostQuery:
        return self._post
    

"""
Manufacturers
"""

class ManufacturerGetQuery(BaseGetQuery):
    api_path = "/api/v1/Manufacturer"
    item_class = Manufacurer
    
    def All(self, page_limit = 25):
        return super().All(page_limit)

    def All_By_Name(self,name, page_limit: int = 25) -> MutableSet[list[Manufacurer], error]:
        items, errs = [], []
        for page, err in PaginateApi(self.List, {"offset":0,"limit":page_limit,"searchTerm":name}):
            if err:
                errs.append(err)
            else:
                items.extend(page)
        if errs:
            return items, f"{self.__class__.__qualname__} All error: {errs}"
        return items, None

class ManufacturerPostQuery(RazorClientDependant):

    def Make_Manufacturer(self, description:str, name:str)-> MutableSet[int, error]:
        base = os.getenv("RAZOR_API")
        url = f"{base}/api/v1/Manufacturer"
        response = self._client.Request("POST",url,data={
            "description": description,
            "name": name, 
        })
        if response.status_code != 200:
            return None, self.error(response)
        
        return int(response.body), None
        
class ManufacturerAPI(RazorClientDependant):
    def __init__(self, client):
        self._get = ManufacturerGetQuery(client)
        self._post = ManufacturerPostQuery(client)
        super().__init__(client)
    
    def Post(self)->ManufacturerPostQuery:
        return self._post
    
    def Get(self) -> ManufacturerGetQuery:
        return self._get

"""
Lookup
"""

class LookupGetQuery(BaseGetQuery):
    api_path = "/api/v1/Lookup"
    


    def Get_Inventory_Categories(self,searchTerm:str=None)->MutableSet[list[InventoryCategory],error]:
        self.item_class = InventoryCategory
        path = "/inventory-categories"
        if searchTerm != None:
            path += f"?term={searchTerm}"
        categories,err = self._fetch_many(path,f"{self.__class__.__qualname__} Get_Inventory_Categories")
        if err != None:
            return None, err
        return categories, None

class LookupAPI(RazorClientDependant):
    def __init__(self, client):
        self._get = LookupGetQuery(client)
        super().__init__(client)
    
    def Get(self)->LookupGetQuery:
        return self._get
    
"""
ItemMaster
"""

class ItemMasterGetQuery(BaseGetQuery):
    api_path = "/api/v1/ItemMaster"
    item_class = ItemMaster

    def By_Name(self,name:str)->MutableSet[list[ItemMaster],error]:
        response = self._client.Request("GET",self._build_url(f"/by-item-number/{name}"))
        if response.status_code != 200:
            return None, self.error(response)
        
        return [build_dataclass(self.item_class,item) for item in response.json()["itemMasters"]],None

class ItemMasterPostQuery(RazorClientDependant):

    def Make_ItemMaster(self,ManufacturerName:str,ItemName:str,AttributeID:int,ManufacturerID:int,PrimaryCategoryID:int,EBayCategoryID:int=None)->MutableSet[int, error]:
        response = self._client.Request("POST",f"{self.api_url}/api/v1/ItemMaster",data={
            "attributeTypeId":AttributeID,
            "eBayCategoryId":EBayCategoryID,
            "manufacturerId":ManufacturerID,
            "primaryCategoryId":PrimaryCategoryID,
            "itemNumber":ItemName,
            "title":f"{ManufacturerName} {ItemName}",
            "itemTypeId":1,
        })
        if response.status_code != 200:
            return None, self.error(response)
        return int(response.body), None

class ItemMasterAPI(RazorClientDependant):
    def __init__(self, client):
        self._get = ItemMasterGetQuery(client)
        self._post = ItemMasterPostQuery(client)
        super().__init__(client)

    def Get(self)->ItemMasterGetQuery:
        return self._get
    
    def Post(self)->ItemMasterPostQuery:
        return self._post












