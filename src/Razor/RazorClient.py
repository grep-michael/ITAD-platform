from datetime import datetime
import hashlib,json,os
import Razor.mureq as mureq
from Razor.helpers import *
from http.cookies import SimpleCookie
from collections.abc import MutableSet
from urllib.parse import urlparse
from Utilities.Config import Config


error = str
AccessToken =  str
AccessResponce = MutableSet[AccessToken, error]
CompanyIDResponse = MutableSet[int, error]

class RazorClient():
    def __init__(self,instance:str=None):
        self.pubToken:str = ""
        self.privToken:str = ""
        self.COOKIES:dict = {}
        self._CACHE:dict = {}
        self.instance:str = instance or os.getenv("RAZOR_INSTANCE")
        self.instanceDomain:str = urlparse(self.instance).netloc

    def Request(self,method:str,url:str,data:dict=None,headers:dict = None,cache:bool = False) -> mureq.Response:
        reqHeaders = {"User-Agent":"ITADBot","Origin":f"{self.instanceDomain}","Accept": "application/json, text/plain, */*"}
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
            return ("",f"Status Invaild: {response.status_code}")
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