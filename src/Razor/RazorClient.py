from datetime import datetime
import hashlib,json,os,types
from typing import Generator
import time
import Razor.mureq as mureq
from Razor.helpers import *
from http.cookies import SimpleCookie
from collections.abc import MutableSet
from urllib.parse import urlparse
from Utilities.Config import Config
from Razor.dataclasses import *
from abc import ABC, abstractmethod

"""
Public token is for the front end ui api
Private Token is for the new backend api razor has started to push out
"""

error = str
AccessToken =  str
AccessResponce = MutableSet[AccessToken, error]
CompanyIDResponse = MutableSet[int, error]

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
        else:
            reqHeaders.update({"Authorization":f"Bearer {self.pubToken}"})
        #if usePriv:
        #    reqHeaders.update({"Authorization":f"Bearer {self.privToken}"})
        #elif usePub:
        #    reqHeaders.update({"Authorization":f"Bearer {self.pubToken}"})
        

        if cache:
            key = hashlib.md5(f"{method}{url}{json.dumps(data, sort_keys=True)}".encode()).hexdigest()
            if key in self._CACHE:
                hit = self._CACHE[key]
                tm:datetime = hit[0]
                if (datetime.now() - tm).total_seconds() < 30:
                    return hit[1]
        
        if headers: reqHeaders.update(headers)
        if self.COOKIES: reqHeaders["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.COOKIES.items())  
        response = mureq.request(method, url, json=data,headers=reqHeaders,**kwargs)
        if cache:
            now = datetime.now()
            self._CACHE[key] = (now,response)
        
        set_cookie = response.headers.get("Set-Cookie")
        if set_cookie:
            cookie = SimpleCookie()
            cookie.load(set_cookie)
            self.COOKIES.update({k: v.value for k, v in cookie.items()})
        #print(method, url)
        #print(response)
        #print(response.body)
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
        self._client:RazorClient = client

PaginatedResponse = MutableSet[PaginatedList, error]
def PaginateApi(fetch: Callable[[int,int],PaginatedResponse], limit: int = 100,**reqArgs) -> Generator[list, None, None]:
    offset = 0
    while True:
        response, err = fetch(offset,limit,**reqArgs)
        if err != None:
            yield None,err
        else:
            yield response.items, None
        offset += limit
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
            return None, f"{label} error: status-{response.status_code}, Body: {response.body}"
        return build_dataclass(self.item_class, response.json()), None
    
    def _fetch_many(self,path:str,label:str,**reqArgs)->list[T]:
        response = self._client.Request("GET",self._build_url(path),**reqArgs)
        if response.status_code != 200:
            return None, f"{label} error: status-{response.status_code}, Body: {response.body}"
        return [ build_dataclass(self.item_class, item) for item in response.json() ], None
    
    def List(self, offset:int=0,limit:int=25,**reqArgs)->PaginatedResponse:
        response = self._client.Request("GET",self._build_url(f"/all?limit={limit}&offset={offset}"),reqArgs)
        if response.status_code != 200:
            return None, f"{self.__class__.__qualname__} List error: status-{response.status_code}, Body: {response.body}"
        return (
            PaginatedList.from_dict(response.json(), item_mapper=lambda d: build_dataclass(self.item_class, d)),
            None
        )
    
    def All(self, page_limit: int = 25) -> MutableSet[list, error]:
        items, errs = [], []
        for page, err in PaginateApi(self.List, limit=page_limit):
            if err:
                errs.append(err)
            else:
                items.extend(page)
        if errs:
            return items, f"{self.__class__.__qualname__} All error: {errs}"
        return items, None


class AssetGetQuery(BaseGetQuery):
    api_path = "/api/v1/Asset"
    item_class = Asset

    def By_UID(self, uid: str) -> MutableSet[list[Asset], error]:
        return self._fetch_many(f"/by-uid/{uid}", f"{self.__class__.__qualname__} By_UID")

    def By_Serial(self, serial: str) -> MutableSet[list[Asset], error]:
        return self._fetch_many(f"/by-serial-number/{serial}", f"{self.__class__.__qualname__} By_Serial")

    def All(self, page_limit: int = 5000):
        return super().All(page_limit)


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

"""
ASSETS
"""

class AssetsAPI(RazorClientDependant):
    def __init__(self, client:RazorClient):
        self.query = AssetGetQuery(client)
        super().__init__(client)

    def Get(self) -> AssetGetQuery:
        return self.query

"""
COMMODITIES
"""

class CommodityAPI(RazorClientDependant):
    def __init__(self, client:RazorClient):
        self.getquery = CommodityGetQuery(client)
        super().__init__(client)

    def Get(self)->CommodityGetQuery:
        return self.getquery