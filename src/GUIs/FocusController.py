from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRect,QObject
from PyQt5.QtGui import QFont,QGuiApplication
from GUIs.BaseWidgets import *

class FocusController():
    def __init__(self,parent:QMainWindow):
        self.parent = parent
    
    def set_focus(self,widget:QWidget,direction:int):

        object_Of_Focus = widget.findChild(QObject,"Object_Of_Focus")
        #if object_Of_Focus is None:
        #    object_Of_Focus = widget.findChild(QListWidget,"Object_Of_Focus")
        
        if not object_Of_Focus:
            #If no Object_Of_Focus
            return
        elif direction == 1:
            #Going forward we always set focus
            object_Of_Focus.setFocus()
        else:
            #going backward we only set focus if the object is a listwidget
            if isinstance(object_Of_Focus,(QListWidget)):
                object_Of_Focus.setFocus()

"""
If going backward dont set any text boxes to focus, if going forward focus text boxes 
"""
    
