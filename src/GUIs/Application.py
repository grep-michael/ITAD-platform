from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRect
from PyQt5.QtGui import QFont,QGuiApplication
import sys,subprocess,re
import xml.etree.ElementTree as ET
from GUIs.WidgetBuilder import *
from GUIs.Overview import Overview
from GUIs.Erasure import *

FONT_FAMILY = "DejaVu Sans"


WIDGET_ORDER = [
    "System_Information/Unique_Identifier",
    "System_Information/Tech_ID",
    "System_Information/System_Category",
    "Devices/Webcam",
    "Devices/Graphics_Controller",
    "Devices/Optical_Drive",
    "Devices/CPU",
    "Devices/Memory",
    "Devices/Display",
    "Devices/Battery",
    "Devices/Storage_Data_Collection",
    "Devices/Storage",
    "System_Information/System_Notes",
    "System_Information/Cosmetic_Grade",
    "System_Information/LCD_Grade",
    "System_Information/Final_Grade",
]

WIDGET_CONDITIONS = {
    "LCD_Grade":(".//System_Information/System_Category",r"Laptop|All-In-One"),
    "Display":(".//System_Information/System_Category",r"Laptop|All-In-One"),
    "Battery":(".//System_Information/System_Category",r"Laptop"),
    "Webcam":(".//System_Information/System_Category",r"Laptop|All-In-One"),
}

class Application(QApplication):

    def calculate_font_factor(self,tree):
        
        screen = QApplication.primaryScreen()
        width = screen.size().width()
        height = screen.size().height()

        dpi = screen.physicalDotsPerInch()
        print("dpi",dpi)
        dpi_factor = dpi/100
        print("dpi_factor",dpi_factor)
        resolution = width * height
        
        reference_resolution = 1920 * 1080

        #scaling_factor = (resolution / reference_resolution) ** 0.5
        scaling_factor = (reference_resolution/resolution) #** 0.5
        print("scaling_factor", scaling_factor)

        min_scale = 0.5  # Won't go smaller than half base size
        max_scale = 3.0  # Won't go larger than 3x base size
        
        scaling_factor = max(min_scale, min(max_scale, scaling_factor))
        print("scaling_factor",scaling_factor)
        font_size = (12*dpi_factor)/scaling_factor
        print(font_size)

        return max(8,font_size)

    def __init__(self,tree):
        super().__init__(sys.argv)
        self.font_factor = self.calculate_font_factor(tree)
        self._font = QFont(FONT_FAMILY)
        self._font.setPointSize(self.font_factor)  # Increase font size
        self.setFont(self._font)

        self.main_window = MainWindow(tree)
        self.main_window.show()

    def run(self):
        self.exec()

class MainWindow(QMainWindow):
    
    def __init__(self,tree):
        super().__init__()
        widget_builder = WidgetBuilder(tree)
        self.widgets = {}
        self.tree = tree

        self.widgets["Devices"] = widget_builder.serve_devices(self)
        self.widgets["System_Information"] = widget_builder.serve_sys_info(self)
        
        self.widget_list = []
        self.widget_index = -1
        self.current_widget = None

        self.build_widget_order()
        
        self.next_widget()

    def build_widget_order(self):
        for widget in WIDGET_ORDER:
            parent,tag = widget.split("/")
            for i in self.widgets[parent][tag]:
                self.widget_list.append(i)
        self.widget_list.append(Overview(self.tree,self))
        self.widget_list.append(ErasureWindow(self.tree))

    def next_widget(self):
        #nuke current widget and its layouts/inner widgets
        central_widget = self.centralWidget()
        if central_widget is not None:
            while central_widget.layout() and central_widget.layout().count() > 0:
                item = central_widget.layout().itemAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                central_widget.layout().removeItem(item)

        self.widget_index+=1
        self.current_widget = self.widget_list[self.widget_index]
        
        if not self.should_show_current_widget():
            self.next_widget()
            return

        #self.check_for_geometry()

        self.pre_update_current_frame()
        self.setCentralWidget(self.current_widget)
        self.adjustSize()
        self.set_focus_to_input()

    def pre_update_current_frame(self):
        if  hasattr(self.current_widget,"pre_display_update"):
            self.current_widget.pre_display_update(self)
    
    #unused
    def check_for_geometry(self):
        
        if "max_width" in dir(self.current_widget):
            self.setMaximumWidth(self.current_widget.max_width)
            #self.setMinimumWidth(self.current_widget.max_width)
        
        if "max_height" in dir(self.current_widget):
            self.setMaximumHeight(self.current_widget.max_height)
            #self.setMinimumHeight(self.current_widget.max_height)

    def should_show_current_widget(self) -> bool:
        """
        Returns if we should display this widget, true=display, false=dont display
        """
        if self.current_widget is None: return True
        if not hasattr(self.current_widget,"element"): return True
        element = self.current_widget.element
        if element.tag in WIDGET_CONDITIONS:
            value = self.tree.find(WIDGET_CONDITIONS[element.tag][0]).text
            regex = WIDGET_CONDITIONS[element.tag][1]
            matches = re.search(regex,value)
            if matches is not None:
                return True
            return False
        return True

    def set_focus_to_input(self):
        """Find and focus the appropriate input widget within the current widget"""
        # Look for QLineEdit first
        line_edits = self.current_widget.findChildren(QLineEdit)
        if line_edits:
            line_edits[0].setFocus()
            return
            
        # Look for QListWidget next
        list_widgets = self.current_widget.findChildren(QListWidget)
        if list_widgets:
            list_widgets[0].setFocus()
            return
        # If no specific widget found, just set focus to the widget itself
        self.current_widget.setFocus()

    #unused
    def get_current_value(self):
        #unused for now
        if isinstance(self.current_widget,CustomList):
            for i in  self.current_widget.children():
                if isinstance(i,QListWidget):
                    print(i.currentItem().text())

    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            no_errors = self.current_widget.verify()
            if no_errors:
                try:
                    self.next_widget()
                except IndexError:
                    print("Quiting")
                    QApplication.instance().quit()
        else:
            super().keyPressEvent(event)



