from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRect,QSize
from PyQt5.QtGui import QFont,QResizeEvent
import sys,subprocess,re
import xml.etree.ElementTree as ET
from GUIs.CustomWidgets import *
from GUIs.BaseWidgets import *
from collections import defaultdict


CLASS_ASSOCIATION = {
    "Webcam":ElementNode,
    "Graphics_Controller":ElementNode,
    "Optical_Drive":ElementNode,
    "CPU":ElementNode,
    "Memory":ElementNode,
    "Display":ElementNode,
    "Battery":ElementNode,
    "Storage":ElementNode,
}

COLUMNS = 3

class Overview(QWidget):
    def __init__(self,tree,parent:'QMainWindow'):
        super().__init__()
        self.tree = tree
        self.parent_window = parent
        
        # Create content widget that will be placed inside scroll area
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.devices = self.build_device_list(self.tree)
        self.content_widget.setLayout(self.build_grid(self.devices))
        
        # Set up scroll area
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content_widget)
        
        # Set main layout to contain the scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        self.setLayout(main_layout)

        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height() - 100
        prefered_height = min(self.content_widget.height(),screen_height)
        self.setFixedHeight(prefered_height)

        self.setMinimumWidth(self.content_widget.sizeHint().width()+10)
        self.max_width = self.content_widget.sizeHint().width()+20
        

    def sizeHint(self):
        # Return the natural size of the content
        if hasattr(self, 'content_widget'):
            content_size = self.content_widget.sizeHint()
            # Add margins for scroll bars if needed
            scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            return QSize(content_size.width() + scrollbar_width, self.height())
        return super().sizeHint()

    def resizeEvent(self,event:QResizeEvent):        
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        screen_height = screen.availableGeometry().height()
        x_position = (screen_width - self.width()) // 2
        y_position = (screen_height - self.height()) // 2
        self.parent().setGeometry(QRect(x_position,y_position,event.size().width(),event.size().height()))

    def build_grid(self,device_list):
        layout = QGridLayout(self)
        order_index = 0
        row = 0
        while 1:
            for c in range(COLUMNS):
                layout.addWidget(device_list[order_index],row,c,alignment=Qt.AlignCenter)
                order_index+=1
                if order_index > len(device_list)-1:
                    break
            row += 1
            if order_index > len(device_list)-1:
                break
        
        return layout

    def build_device_list(self,tree):
        devices = tree.find(".//SYSTEM_INVENTORY/Devices")
        #device_list = defaultdict(list)
        device_list = []
        for device in devices:
            #device_list[device.tag].append( CLASS_ASSOCIATION[device.tag](device,font_fac))
            if device.tag in CLASS_ASSOCIATION:
                device_list.append(CLASS_ASSOCIATION[device.tag](device,None))
        return device_list

    def verify(self):
        return True
    
