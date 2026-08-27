from dataclasses import dataclass
from typing import Optional

"""
ManufacturerID must be made/got separately
Weights are in pounds
"""


@dataclass(frozen=True)
class CommodityData:
    XMLName: str
    RazorCommodityID: int
    Weight: float
    RazorAttributeID: int
    RazorPrimaryCategory: int
    EBayCategoryID: Optional[int] = None
    #ManufacturerID: Optional[int] = None #removed because it doesnt fit the static nature of the rest of the data

RAM           = CommodityData(".//Memory_Device", 52, 0.1, 9, 380)
CPU           = CommodityData(".//CPU", 381, 0.31, 24, 245)
POWER_SUPPLY  = CommodityData(".//Power_Supply", 306, 2.2, 15, 249)
#NETWORK_CARD  = CommodityData(".//Slot_1", 451, 0.2, 7, 217) #Finger Boards
NETWORK_CARD  = CommodityData(".//Slot_1", 981, 0.2, 7, 217)




CommodityList = [
    RAM,
    CPU,
    POWER_SUPPLY,
    NETWORK_CARD,
]