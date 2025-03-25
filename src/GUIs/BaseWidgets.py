
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from Utils.InputVerification import Verifier
import xml.etree.ElementTree as ET


class CustomList(QWidget):
    def __init__(self,element:ET.Element,options:list,friendly_label:str,parent:QWidget,default_option=0):
        super().__init__()
        self.element = element
        self.vbox = QVBoxLayout()

        self.build_label(friendly_label)
        self.build_ListWidget(options,element,default_option)
        self.vbox.addStretch()
        self.setLayout(self.vbox)
        self.max_height = self.height()
        self.max_width = self.width()
        

    def build_label(self,friendly_label):
        wlabel = QLabel(friendly_label)
        height = QFontMetrics(wlabel.font()).height() 
        #wlabel.setFixedHeight(height)
        wlabel.setMinimumHeight(height)
        self.vbox.addWidget(wlabel)

    def build_ListWidget(self,options,element,default_option):
        wlist = QListWidget()
        height = QFontMetrics(wlist.font()).height() * (len(options)+1)
        #wlist.setFixedHeight(height)
        wlist.setMinimumHeight(height)
        wlist.addItems(options)

        #set current item after you connect the signal
        wlist.currentTextChanged.connect(lambda text, element=element: self.text_changed(element,text))
        wlist.setCurrentItem(wlist.item(default_option))

        self.vbox.addWidget(wlist)

    def text_changed(self, el,s):
        #print("text changed",el,s)
        el.text = s
    
    def verify(self):
        return True

    def setFocus(self):
        # Override setFocus to focus the list widget
        if self.list_widget:
            self.list_widget.setFocus()
        else:
            super().setFocus()


class XmlQLineEdit(QLineEdit):
    """
    Literally just used for python type strings and for vscode python auto complete
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.associated_xml = None

class ElementNode(QWidget):
    def __init__(self,el,parent):#,font_factor=5):
        super().__init__()
        self.element = el
        #self.font_factor = font_factor
        self.vbox = QVBoxLayout()

        if len(list(self.element)) == 0:
            self.format_no_subnodes()
        else:
            self.format_with_subnodes()
        self.setLayout(self.vbox)
        self.max_height = self.calc_height()

    def calc_height(self):        
        height = 0
        for i in range(self.vbox.count()):
            child = self.vbox.itemAt(i)
            try:
                height+= QFontMetrics(child.font()).height()#+self.font_factor
            except:
                height+= child.minimumSize().height()#+self.font_factor

        return height

    def verify(self) -> bool:
        """
        Returns:
            True if no errors
            False if Errors
        """
        verifier = Verifier(self.element.tag)
        errors = []
        for child in self.children():
            if isinstance(child, QLineEdit):                
                verified = verifier.verifify(child)
                if verified:
                    child.setStyleSheet("border: 2px solid green;")
                else:
                    child.setStyleSheet("border: 2px solid red;")
                    errors.append(True)

        return len(errors)==0
    
    def setFocus(self):
        # Override setFocus to focus the first line edit
        line_edits = self.findChildren(QLineEdit)
        if line_edits:
            line_edits[0].setFocus()
        else:
            super().setFocus()

    def text_changed(self,text_widget:QLineEdit):

        text_widget.associated_xml.text = text_widget.text()

    def format_with_subnodes(self):
        label = QLabel(self.element.tag.replace("_"," "))
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.vbox.addWidget(label)
        max_size = 0
        for child in self.element:
            row = QHBoxLayout()
            label = QLabel(child.tag)
            row.addWidget(label)
            

            text_display = QLineEdit(self)
            text_display.associated_xml = child
            text_display.textEdited.connect(lambda _, tb=text_display: self.text_changed(tb))
            text_display.setText(child.text)

            size = QFontMetrics(text_display.font()).horizontalAdvance(text_display.text())+7 #+ self.font_factor
            size = min(size,500)
            max_size = max(size,max_size)
            
            text_display.setMinimumWidth(size)
            
            
            row.addWidget(text_display)
            
            self.vbox.addLayout(row)

        self.max_width = max_size

    def format_no_subnodes(self):
        label = QLabel(self.element.tag.replace("_"," "))

        #height = QFontMetrics(label.font()).height()+2 #* self.font_factor
        #label.setMinimumHeight(height)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.vbox.addWidget(label)

        text_display = XmlQLineEdit()
        text_display.associated_xml = self.element
        text_display.textEdited.connect(lambda _, tb=text_display: self.text_changed(tb))
        text_display.setText(self.element.text)


        if len(text_display.text()) > 1:
            size = QFontMetrics(text_display.font()).horizontalAdvance(text_display.text())+7 #+ self.font_factor
        else:
            size = label.widthMM()
        size = min(size,500)
        
        #text_display.setFixedWidth(size)
        #text_display.setFixedHeight(QFontMetrics(text_display.font()).height())

        text_display.setMinimumWidth(size)
        #text_display.setMinimumHeight(QFontMetrics(text_display.font()).height()) 

        self.max_width = size

        self.vbox.addWidget(text_display)

