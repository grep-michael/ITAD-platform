from PyQt5.QtWidgets import QWidget,QFrame
from PyQt5.QtCore import QObject

class ITADController(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        """
        Base controller class for all controllers
        """
        self.view:QWidget

    
    def verify(self):
        """
        Called in the main window when the program tries to move to the next widget 
        """
        raise NotImplementedError()

    def pre_display_update(self,parent):
        """
        Called before the widget is set as the current widget in the main window
        """
        return

class ITADView(QWidget):
    """
    Base class for all views
    """
    def __init__(self):
        super().__init__()
        self.has_been_viewed = False
        
    
