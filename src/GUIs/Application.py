from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRect
from PyQt5.QtGui import QFont,QGuiApplication
import sys,subprocess,re
#from GUIs.FocusController import FocusController
import xml.etree.ElementTree as ET
from GUIs.WidgetBuilder import *
from GUIs.CustomWidgets.CustomWidgets import ExitWindow

FONT_FAMILY = "DejaVu Sans"

#WIDGET_ORDER = [
#    "System_Information/Unique_Identifier",
#    "System_Information/Tech_ID",
#    "System_Information/System_Category",
#    "Devices/Webcam",
#    "Devices/Graphics_Controller",
#    "Devices/Optical_Drive",
#    "Devices/CPU",
#    "Devices/Memory",
#    "Devices/Display",
#    "Devices/Battery",
#    "Devices/Storage_Data_Collection",
#    "Devices/Storage",
#    "System_Information/System_Notes",
#    "System_Information/Cosmetic_Grade",
#    "System_Information/LCD_Grade",
#    "System_Information/Final_Grade",
#]

WIDGET_CONDITIONS = {
    "LCD_Grade":(".//System_Information/System_Category",r"Laptop|All-In-One"),
    "Display":(".//System_Information/System_Category",r"Laptop|All-In-One"),
    "Battery":(".//System_Information/System_Category",r"Laptop"),
    "Webcam":(".//System_Information/System_Category",r"Laptop|All-In-One"),
}

class Application(QApplication):

    def calculate_font_factor(self,tree):
        """
        idk how this works but it does, kinda, what do i look like a computer scientist?
        """
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
        print("calculated font size",font_size)

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
    
    def __init__(self,tree:ET.Element):
        super().__init__()
        widget_builder = WidgetBuilder(tree)
        self.logger = logging.getLogger("MainWindow")
        self.focus_controller = FocusController(self)
        self.tree:ET.Element = tree
        
        self.widget_list = widget_builder.build_widget_list(self)
        self.widget_index = -1
        self.current_widget:ITADWidget = None
        
        self.next_widget()
    
    def switch_widget(self,direction:int=1):
        if direction not in [-1,1]:
            self.logger.warning("switch widget recived unexpected input direction: {}".format(direction))
            return
        last_widget = self.takeCentralWidget() #removes centralWidget without destorying it
        if last_widget:
            last_widget.has_been_viewed = True
        self.widget_index += direction
        if self.widget_index < 0 or self.widget_index > len(self.widget_list):
            self.widget_index -= direction
            #self.logger.warning("widget_index out of bounds")
            return
        
        
        self.current_widget = self.widget_list[self.widget_index]
        
        if not self.should_show_current_widget():
            self.switch_widget(direction)
            return

        #self.check_for_geometry()
        
        if hasattr(self.current_widget,"pre_display_update"):
            self.current_widget.pre_display_update(self)

        
        self.setCentralWidget(self.current_widget)
        self.adjustSize()
        self.focus_controller.set_focus(self.current_widget,direction)
        #self.set_focus_to_input()
        
    def previous_widget(self):
        self.switch_widget(-1)

    def next_widget(self):
        self.switch_widget()
        if isinstance(self.centralWidget(),ExitWindow):
            self.logger.info("centralWidget is ExitWindow ... Exiting")
            print("Quitting")
            QCoreApplication.instance().quit()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter or event.key() == Qt.Key_Right:
            no_errors = self.current_widget.verify()
            if no_errors:
                self.next_widget()
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Left:
            self.current_widget.verify()
            self.previous_widget()
        
        elif event.key() ==  Qt.Key_Escape:
            self.setFocus()
        
        else:
            super().keyPressEvent(event)

    def resizeEvent(self,event:QResizeEvent):
        """
        Centers window whenever the centraled widget is changes
        """
        screen = QApplication.primaryScreen()
        screen_width = screen.availableGeometry().width()
        screen_height = screen.availableGeometry().height()
        x_position = (screen_width - self.width()) // 2
        y_position = (screen_height - self.height()) // 2
        self.setGeometry(QRect(x_position,y_position,event.size().width(),event.size().height()))

class FocusController():
    def __init__(self,parent:QMainWindow):
        self.parent = parent
    
    def set_focus(self,widget:ITADWidget,direction:int):

        object_Of_Focus = widget.findChild(QObject,"Object_Of_Focus")

        if not object_Of_Focus:
            #If no Object_Of_Focus
            return
        elif direction == 1:
            #Going forward we always set focus
            if not widget.has_been_viewed:
                object_Of_Focus.setFocus()
        else:
            #going backward we only set focus if the object is a listwidget
            if isinstance(object_Of_Focus,(QListWidget)):
                object_Of_Focus.setFocus()