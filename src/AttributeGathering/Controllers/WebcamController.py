from AttributeGathering.Controllers.BasicNodeController import BasicNodeController
import xml.etree.ElementTree as ET

class WebcamController(BasicNodeController):
    def __init__(self, element:ET.Element):
        super().__init__(element)