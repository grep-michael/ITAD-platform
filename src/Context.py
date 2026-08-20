from dataclasses import dataclass, field
from collections import defaultdict
import xml.etree.ElementTree as ET
from Razor.RazorClient import RazorClient
from typing import Protocol

class FatalError(Exception):
    """Exit"""

@dataclass
class ErrorField:
    name: str
    value: str

@dataclass
class Error:
    Message:str
    Fields:list[ErrorField] = None

@dataclass
class Context:
    root: ET.Element = None
    client: RazorClient = None
    asset: object = None
    serial: str = None
    UID: str = None
    Commodities:dict[str,list] = field(default_factory=lambda: defaultdict(list))
    errors: list[Error] = field(default_factory=list)

    def fail(self, err:Error):
        self.errors.append(err)

    def add_commodity(self, name: str, uid: str) -> None:
        self.Commodities[name].append(uid)

class Step(Protocol):
    name: str
    def run(self,ctx:Context) -> None: ...