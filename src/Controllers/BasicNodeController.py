from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot,QObject
import xml.etree.ElementTree as ET
from Views.BasicNodeView import BasicNodeView
from Generics import ITADController,ITADView
from Utilities.InputVerification import Verifier


class BasicNodeController(ITADController):
    def __init__(self,element:ET.Element):
        super().__init__()
        self.element = element
        
    def handle_text_box_edit(self,txt_box:QLineEdit):
        if txt_box.objectName() == self.element.tag:
            self.element.text = txt_box.text()
        else:
            self.element.find(txt_box.objectName()).text = txt_box.text()
        
    def connect_view(self,view:ITADView):
        self.view:BasicNodeView = view
        self.view.build_from_element(self.element)
        
        for txt_box in self.view.text_boxes:
            txt_box.textEdited.connect(
                lambda _, tb=txt_box: self.handle_text_box_edit(tb)
            )

    def verify(self) -> bool:
        
        """
        Returns:
            True if no errors
            False if Errors
        """

        verifier = Verifier(self.element.tag)
        errors = []

        def verify_recusive(widget:QObject):
            for child in widget.children():
                if isinstance(child, QLineEdit):                
                    verified = verifier.verifify(child,child.objectName())
                    if verified:
                        child.setStyleSheet("border: 2px solid green !important;")
                    else:
                        child.setStyleSheet("border: 2px solid red !important;")
                        errors.append(True)
                else:
                    verify_recusive(child)
            return
        
        verify_recusive(self.view)

        return len(errors)==0
    
    def setFocus(self):
        # Override setFocus to focus the first line edit
        line_edits:list[QLineEdit] = self.view.findChildren(QLineEdit)
        if line_edits:
            line_edits[0].setFocus()
        else:
            self.view.setFocus()