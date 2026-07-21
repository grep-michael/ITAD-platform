
from dataclasses import dataclass,field
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
    id: Optional[int] = None
    itemMasterId: Optional[int] = None
    inventoryId: Optional[int] = None
    serial: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    locationFullName: Optional[str] = None
    customer: Optional[str] = None
    customerId: Optional[int] = None
    lotId: Optional[int] = None
    lotAutoName: Optional[str] = None
    recyclingOrderId: Optional[int] = None
    recyclingOrderAutoName: Optional[str] = None
    assetWorkflowStep: Optional[str] = None  # keep only this one
    assetWorkflowStepId: Optional[int] = None
    attributeSet: Optional[str] = None
    attributeSetId: Optional[int] = None
    category: Optional[str] = None
    categoryId: Optional[int] = None
    categoryName: Optional[str] = None
    conditionId: Optional[int] = None
    warehouseId: Optional[int] = None
    quantity: Optional[int] = None
    uniqueId: Optional[str] = None
    isUnique: Optional[bool] = False
    itemStatusId: Optional[int] = None
    locationId: Optional[int] = None
    manufacturerId: Optional[int] = None
    modelId: Optional[int] = None
    priceTypeId: Optional[int] = None
    weight: Optional[float] = None
    gradeLevelMarkCalc: Optional[str] = None
    dateCreated: Optional[str] = None
    updatedDate: Optional[str] = None
    auditedDate: Optional[str] = None
    reference: Optional[str] = None
    attributes: Optional[list[Attribute]] = None
    assetSettlementCosts: Optional[list[SettlementCost]] = None
    dataDestruction: Optional[list[DataDestruction]] = None
    assetTag: Optional[str] = None
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

@dataclass
class Account:
    id: Optional[int] = None
    typeId: Optional[int] = None
    typeName: Optional[str] = None


@dataclass
class CommodityTag:
    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class StateProgram:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    activeSinceDt: Optional[str] = None
    inactiveSinceDt: Optional[str] = None
    insertedDt: Optional[str] = None
    updatedDt: Optional[str] = None
    isInactive: Optional[bool] = None
    contractedWeight: Optional[float] = None
    soldWeight: Optional[float] = None
    qtyCategories: Optional[int] = None
    qtyCommodities: Optional[int] = None
    qtyContracts: Optional[int] = None
    qtyInboundOrders: Optional[int] = None
    qtyLots: Optional[int] = None


@dataclass
class Manufacurer:
    id:int = None
    name:str = None

@dataclass
class InventoryCategory:
    fullName:str  = None
    fullPath:str = None
    id:int = None
    name:str = None
    taxCode:str = None

@dataclass
class ItemCategory:
    id: Optional[int] = None
    name: Optional[str] = None
    fullName: Optional[str] = None
    isPrimary: Optional[bool] = None

@dataclass
class ItemMaster:
    id: Optional[int] = None
    itemNumber: Optional[str] = None
    title: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturerId: Optional[int] = None
    attributeType: Optional[str] = None
    attributeTypeId: Optional[int] = None
    itemTypeId: Optional[int] = None
    primaryCategoryId: Optional[int] = None
    eBayCategoryId: Optional[int] = None
    externalId: Optional[str] = None
    harmonizationCode: Optional[str] = None
    ipn: Optional[str] = None
    mpn: Optional[str] = None
    whiteLabel: Optional[str] = None
    isActive: Optional[bool] = None
    isDiscontinued: Optional[bool] = None

    accounts: list[Account] = field(default_factory=list)
    categories: list[ItemCategory] = field(default_factory=list)
    tags: list[CommodityTag] = field(default_factory=list)
    codes: list[str] = field(default_factory=list)
    eccnCodes: list[str] = field(default_factory=list)

@dataclass
class Commodity:
    id: int
    name: str
    groupId: int
    description: str
    requiresCount: bool
    requiresNotes: bool
    requiresReference: bool
    isEnabled: Optional[bool] = None

    category: Optional[str] = None
    categoryId: Optional[int] = None
    categoryFullPath: Optional[str] = None
    code: Optional[str] = None
    groupName: Optional[str] = None
    alternativeName: Optional[str] = None
    businessUnitId: Optional[int] = None
    classTrackingPrice: Optional[float] = None
    defaultCount: Optional[int] = None
    defaultWorkflowName: Optional[str] = None
    defaultWorkflowTypeId: Optional[int] = None
    externalId: Optional[str] = None
    isHazardous: Optional[bool] = None
    isInactive: Optional[bool] = None
    isNonStateProgram: Optional[bool] = None
    isUniversalWaste: Optional[bool] = None
    materialStreamTypeId: Optional[str] = None
    uses: Optional[int] = None

    accounts: list[Account] = field(default_factory=list)
    stateProgramAccounts: list[Account] = field(default_factory=list)
    statePrograms: list[StateProgram] = field(default_factory=list)
    commodityTags: list[CommodityTag] = field(default_factory=list)
    tags: list[CommodityTag] = field(default_factory=list)

@dataclass
class SortingItem:
    RecyclingOrderItemId: Optional[int] = None
    ParentId: Optional[int] = None
    ParentsKey: Optional[str] = None
    RecyclingOrderId: Optional[int] = None
    ItemAutoName: Optional[str] = None
    ItemTypeId: Optional[int] = None
    ItemTypeCD: Optional[str] = None
    CommodityId: Optional[int] = None
    CommodityName: Optional[str] = None
    LocationId: Optional[int] = None
    LocationCD: Optional[str] = None
    WarehouseId: Optional[int] = None
    WarehouseCD: Optional[str] = None
    BusinessUnitId: Optional[int] = None
    BusinessUnitName: Optional[str] = None
    PackagingTypeId: Optional[int] = None
    PackagingTypeCD: Optional[str] = None
    WorkflowTypeId: Optional[int] = None
    WorkflowTypeCD: Optional[str] = None
    Level: Optional[int] = None
    Weight: Optional[float] = None
    Tare: Optional[float] = None
    Net: Optional[float] = None
    RemainWeight: Optional[float] = None
    ItemCount: Optional[int] = None
    SequentialNumber: Optional[int] = None
    Notes: Optional[str] = None
    Reference: Optional[str] = None
    CustomerName: Optional[str] = None
    LotId: Optional[int] = None
    LotAutoName: Optional[str] = None
    AlternativeLotName: Optional[str] = None
    GroupId: Optional[int] = None
    GroupName: Optional[str] = None
    ContractId: Optional[int] = None
    InboundOrderName: Optional[str] = None
    StateProgramId: Optional[int] = None
    StateProgramCd: Optional[str] = None
    StateProgramName: Optional[str] = None
    DataRequirementsType: Optional[str] = None
    DataRequirementsTypeId: Optional[int] = None
    MaterialStreamType: Optional[str] = None
    MaterialStreamTypeId: Optional[int] = None
    MainInnerLotInMergeId: Optional[int] = None
    SubstitutionLotId: Optional[int] = None
    ImageCount: Optional[int] = None
    CountInGroup: Optional[int] = None
    UserId: Optional[int] = None
    UserName: Optional[str] = None
    ExportedDate: Optional[str] = None
    ReceiveDate: Optional[str] = None
    IsLeaf: Optional[bool] = None
    IsProcessed: Optional[bool] = None
    Expanded: Optional[bool] = None
    IsCertifiedDestruction: Optional[bool] = None
    IsHazardousWaste: Optional[bool] = None
    IsUniversalWaste: Optional[bool] = None
    IsMergePrimary: Optional[bool] = None
    IsPartOfMerged: Optional[bool] = None
    RequiresCount: Optional[bool] = None
    RequiresNotes: Optional[bool] = None
    RequiresReference: Optional[bool] = None
    WorkInstructions: Optional[str] = None


@dataclass
class SortingItemsResponse:
    page: Optional[int] = None
    total: Optional[int] = None
    records: Optional[int] = None
    rowNum: Optional[int] = None
    CustomTotalQty: Optional[int] = None
    UserRole: Optional[str] = None
    rows: Optional[list[SortingItem]] = None

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