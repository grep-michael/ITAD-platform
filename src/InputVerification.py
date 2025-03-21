import re
from PyQt5.QtWidgets import *
from Utils import REGEX_ERROR_MSG

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from GUIs.WidgetBuilder import XmlQLineEdit


WHITE_LIST = {
    #"Unique_Identifier":r"^(\w{2}[\w\d]{8})$",
    
    "CPU":{ #example for sub elements
        "Family":r".*", #will pass on everything
    }
}

class Verifier():
    def __init__(self,element_path:str):
        self.element_path = element_path
    
    def verifify(self,widget:'XmlQLineEdit') -> bool:
        """
        Returns:
            True if text is valid
            False if text is not valid
        """
        #order of checking is important here
        if REGEX_ERROR_MSG in widget.text():
            #text matches the error for ErrorLessRegex, fail
            return False
        
        if self.element_path not in WHITE_LIST:
            #no regex defined for this node, success
            return True
        
        regex = WHITE_LIST[self.element_path]

        if isinstance(regex,dict): #has sub nodes
            if widget.associated_xml.tag not in regex: 
                return True #if sub node doesnt have a regex pass
            regex = regex[widget.associated_xml.tag]

        return self.search(regex,widget)
        
    def search(self,regex,widget:'XmlQLineEdit'):
            matches = re.search(regex,widget.text())
            if matches is not None:
                    #xml text matches whitelist, success
                return True
            return False
        