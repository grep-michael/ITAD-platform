from PyQt5.QtWidgets import QWidget,QFrame
from PyQt5.QtCore import QObject
import xml.etree.ElementTree as ET

class ITADView(QWidget):
    """
    Base class for all views
    """
    def __init__(self):
        super().__init__()
        self.has_been_viewed = False

class ITADController(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        """
        Base controller class for all controllers
        """
        self.view:ITADView
        self.element:ET.Element
    
    def connect_view(self,view:ITADView):
        self.view = view

    
    def verify(self):
        """
        Called in the main window when the program tries to move to the next widget 
        """
        return True

    def pre_display_update(self,parent):
        """
        Called before the widget is set as the current widget in the main window
        """
        return

    def setFocus(self):
        if self.view != None:
            return self.view.setFocus()
        return

    def adjustSize(self):
        if self.view != None:
            return self.view.adjustSize()
        return

        
    
