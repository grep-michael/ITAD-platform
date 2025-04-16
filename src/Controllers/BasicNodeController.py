from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot,QObject
import xml.etree.ElementTree as ET
from Views.BasicNodeView import BasicNodeView
from Generics import ITADView
from Utilities.InputVerification import Verifier


class BasicNodeController(ITADView):
    def __init__(self,element:ET.Element):
        super().__init__()
        self.element = element
        self.initUI()
    
    def initUI(self):
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.build_view()
        self.connect_view()
    
    def build_view(self):
        self.view = BasicNodeView()
        self.view.build_from_element(self.element)

    def text_box_edited(self,txt_box:QLineEdit):
        if txt_box.objectName() == self.element.tag:
            self.element.text = txt_box.text()
        else:
            self.element.find(txt_box.objectName()).text = txt_box.text()
        
    def connect_view(self):
        self.vbox.addWidget(self.view)
        self.adjustSize()
        for txt_box in self.view.text_boxes:
            txt_box.textEdited.connect(
                lambda _, tb=txt_box: self.text_box_edited(tb)
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
        
        verify_recusive(self)

        return len(errors)==0
    
    def setFocus(self):
        # Override setFocus to focus the first line edit
        line_edits = self.findChildren(QLineEdit)
        if line_edits:
            line_edits[0].setFocus()
        else:
            super().setFocus()