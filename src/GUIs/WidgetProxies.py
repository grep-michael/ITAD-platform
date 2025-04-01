"""
proxy classes for easily changing widget functionality without having to mess with WidgetBuilder,
goal is to pass as much info as any widget might need to the proxy and let the proxy build an actual widget
"""
from PyQt5.QtWidgets import *
from GUIs.CustomWidgets import *
from GUIs.BaseWidgets import *
import xml.etree.ElementTree as ET


class DefaultProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return ElementNode(element)


class UUIDProxy(DefaultProxy):
    pass
class TechIDProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return TechIDList(element)
    
class CategoryProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return SystemCategory(element)
class WebcamProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return WebCam(element)
    
class GraphicsControllerProxy(DefaultProxy):
    pass
class OpticalDriveProxy(DefaultProxy):
    pass
class CPUProxy(DefaultProxy):
    pass
class MemoryProxy(DefaultProxy):
    pass
class DisplayProxy(DefaultProxy):
    pass
class BatteryProxy(DefaultProxy):
    pass
class StorageProxy(DefaultProxy):
    pass

class SystemNotesProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return NotesWidget(parent,element)
class CosmeticGradeProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return GradeList(element)
class LCDGradeProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return GradeList(element)
class FinalGradeProxy:
    def get_host(parent,tree_root:ET.Element,element:ET.Element):
        return FinalGrade(element)
