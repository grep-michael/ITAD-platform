
from dataclasses import dataclass
import dataclasses
from typing import Optional,get_args, get_origin, Union,Generic,TypeVar,Callable
import json

#ai generated, human reviewed
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



T = TypeVar("T")
@dataclass
class PaginatedList(Generic[T]):
    items: list[T]
    records: int
    total_records: int

    @classmethod
    def from_dict(cls, data: dict, 
                  item_mapper: Callable[[dict], T] = lambda x: x
                ) -> "PaginatedList[T]":
        return cls(
            items=[item_mapper(i) for i in data["items"]],
            records=data["records"],
            total_records=data["totalCount"],
        )

    @property
    def is_last(self) -> bool:
        return len(self.items) == 0 or self.records >= self.total_records

def build_dataclass(cls, data: dict):
    """Recursively build a dataclass from a dict, ignoring unknown keys."""
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")

    kwargs = {}
    field_map = {f.name: f for f in dataclasses.fields(cls)}

    for name, field in field_map.items():
        if name not in data:
            continue

        value = data[name]
        kwargs[name] = _coerce(field.type, value)

    return cls(**kwargs)


def _coerce(typ, value):
    """Coerce a raw value into the expected type, handling nested dataclasses and lists."""
    if value is None:
        return None

    # Unwrap Optional[X] -> X
    if get_origin(typ) is Union:
        inner = [a for a in get_args(typ) if a is not type(None)]
        if inner:
            return _coerce(inner[0], value)

    # Handle list[SomeDataclass]
    if get_origin(typ) is list:
        inner = get_args(typ)
        item_type = inner[0] if inner else None
        if item_type and dataclasses.is_dataclass(item_type):
            return [build_dataclass(item_type, i) for i in (value or [])]
        return value

    # Recursively build nested dataclasses
    if dataclasses.is_dataclass(typ) and isinstance(value, dict):
        return build_dataclass(typ, value)

    return value