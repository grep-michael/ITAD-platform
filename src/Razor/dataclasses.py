
from dataclasses import dataclass
import dataclasses
from typing import Optional
import json

@dataclass
class SettlementCost:
    assetId: int
    auditExpense: float
    dataDestructionExpense: float
    erasureExpense: float
    miscOverhead: float
    otherExpense: float
    priceToVendor: float
    shippingCost: float

@dataclass
class Attribute:
    typeName: str
    value: str

@dataclass
class DataDestruction:
    id: int
    itemMasterId: int
    serial: str
    model: str
    mfg: str
    hddType: str
    capacity: str
    source: str
    employee: str
    interface: Optional[str]
    formFactor: Optional[str]
    erasureMethod: Optional[str]
    erasureStatus: Optional[str]
    destructionMethod: Optional[str]
    destructionDate: Optional[str]
    date: Optional[str]

@dataclass
class Asset:
    id: int
    inventoryId: int
    serial: str
    manufacturer: str
    model: str
    condition: str
    location: str
    locationFullName: str
    customer: str
    customerId: int
    lotId: int
    lotAutoName: str
    recyclingOrderId: int
    recyclingOrderAutoName: str
    assetWorkflowStep: str
    assetWorkflowStepId: int
    attributeSet: str
    attributeSetId: int
    category: str
    categoryId: int
    categoryName: str
    conditionId: int
    warehouseId: int
    quantity: int
    uniqueId: str
    isUnique: bool
    itemStatusId: int
    locationId: int
    manufacturerId: int
    modelId: int
    priceTypeId: int
    weight: float
    gradeLevelMarkCalc: str
    dateCreated: str
    updatedDate: str
    auditedDate: str
    reference: str
    attributes: list[Attribute]
    assetSettlementCosts: list[SettlementCost]
    dataDestruction: list[DataDestruction]
    assetTag: Optional[str] = None
    assetWorkflowStep: Optional[str]
    commodity: Optional[str] = None
    commodityId: Optional[int] = None
    designatedDataErasureMethod: Optional[str] = None
    finalGradeLevel: Optional[str] = None
    floorPrice: Optional[float] = None
    ipn: Optional[str] = None
    mpn: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[float] = None
    recyclingWorkflowStep: Optional[str] = None
    recyclingWorkflowStepId: Optional[int] = None




def _make(cls, data: dict):
    known = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in known})

def build_asset(data: dict) -> Asset:
    return Asset(
        **{k: v for k, v in data.items() if k not in ("attributes", "assetSettlementCosts", "dataDestruction")
           and k in {f.name for f in dataclasses.fields(Asset)}},
        attributes=[_make(Attribute, a) for a in data.get("attributes", [])],
        assetSettlementCosts=[_make(SettlementCost, s) for s in data.get("assetSettlementCosts", [])],
        dataDestruction=[_make(DataDestruction, d) for d in data.get("dataDestruction", [])],
    )