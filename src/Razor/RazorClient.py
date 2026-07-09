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

    def Request(self,
                method:str,url:str,
                data:dict=None,
                headers:dict=None,
                cache:bool=False,
                usePriv:bool=False,
                usePub:bool=False,
            ) -> mureq.Response:
        reqHeaders = {"User-Agent":"ITADBot","Origin":f"{self.instanceDomain}","Accept": "application/json, text/plain, */*"}
        
        if usePriv:
            reqHeaders.update({"Authorization":f"Bearer {self.privToken}"})
        elif usePub:
            reqHeaders.update({"Authorization":f"Bearer {self.pubToken}"})
        

        if cache:
            key = hashlib.md5(f"{method}{url}{json.dumps(data, sort_keys=True)}".encode()).hexdigest()
            if key in self._CACHE:
                hit = self._CACHE[key]
                tm:datetime = hit[0]
                if (datetime.now() - tm).total_seconds() < 30:
                    return hit[1]
        
        if headers: reqHeaders.update(headers)
        if self.COOKIES: reqHeaders["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.COOKIES.items())  
        response = mureq.request(method, url, json=data,headers=reqHeaders)
        if cache:
            now = datetime.now()
            self._CACHE[key] = (now,response)
        
        set_cookie = response.headers.get("Set-Cookie")
        if set_cookie:
            cookie = SimpleCookie()
            cookie.load(set_cookie)
            self.COOKIES.update({k: v.value for k, v in cookie.items()})
        
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
def PaginateApi(fetch: Callable[[int,int],PaginatedResponse ], limit: int = 100) -> Generator[list, None,None]:
    offset = 0
    while True:
        response, err = fetch(offset,limit)
        print(offset)
        if err != None:
            break
        yield response.items
        offset += limit
        if offset >= response.total_records or len(response.items) == 0:
            break
        


AssetRequest = MutableSet[list[Asset], error]

class AssetGetQuery(RazorClientDependant):
    def __init__(self,client:RazorClient):
        self._api = os.getenv("RAZOR_API")
        super().__init__(client)
    
    def By_UID(self,uid:str)->AssetRequest:
        response = self._client.Request("GET",f"{self._api}/api/v1/Asset/by-uid/{uid}",usePriv=True)
        if response.status_code != 200:
            return (None,f"Status Invaild getting asset by uid: {response.status_code}-{response.body}")
        assets: list[Asset] = [build_dataclass(Asset,item) for item in json.loads(response.body)]
        return (assets,None)
    
    def By_Serial(self,serial:str)->AssetRequest:
        response = self._client.Request("GET",f"{self._api}/api/v1/Asset/by-serial-number/{serial}",usePriv=True)
        if response.status_code != 200:
            return (None,f"Status Invaild getting asset by serial: {response.status_code}-{response.body}")
        assets: list[Asset] = [build_dataclass(Asset,item) for item in json.loads(response.body)]
        return (assets,None)

    def List(self, offset:int=0, limit:int=25)->MutableSet[PaginatedList, error]:
        response = self._client.Request("GET",f"{self._api}/api/v1/Asset/all?limit={limit}&offset={offset}",usePriv=True,timeout=300)
        if response.status_code != 200:
            return (None,f"Status Invaild listing offset: {response.status_code}-{response.body}")
        return (
            PaginatedList.from_dict(
                response.json(),
                item_mapper= lambda d: build_dataclass(Asset,d)
            ),
            None
        )
    """
    Warning this will take awhile if you have alot of Assets
    """
    def All(self):
        pages = [x for x in PaginateApi(self.List,limit=5000)]
        print(len(pages))
        return ([],None)


class AssetsAPI(RazorClientDependant):
    def __init__(self, client:RazorClient):
        self.query = AssetGetQuery(client)

        super().__init__(client)

    def Get(self) -> AssetGetQuery:
        return self.query