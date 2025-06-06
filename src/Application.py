from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRect,QCoreApplication,QObject
from PyQt5.QtGui import QFont,QResizeEvent,QKeyEvent

import sys,re,logging
import xml.etree.ElementTree as ET
from Services.ControllerListFactory import ControllerListFactory
from AttributeGathering.Views.ExitWindowView import ExitWindow
from Generics import *
from WidgetConditions import *
from Utilities.Config import Config
from AttributeGathering.Controllers.BasicListController import BasicListController


FONT_FAMILY = "DejaVu Sans"


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

        scaling_factor = (resolution / reference_resolution) ** 0.5
        scaling_factor = (reference_resolution/resolution) #** 0.5
        print("scaling_factor", scaling_factor)

        min_scale = 0.5  # Won't go smaller than half base size
        max_scale = 3.0  # Won't go larger than 3x base size
        
        scaling_factor = max(min_scale, min(max_scale, scaling_factor))
        print("scaling_factor",scaling_factor)
        font_size = (12*dpi_factor)/scaling_factor
        print("calculated font size",font_size)

        return max(10,font_size)

    def __init__(self,tree):
        super().__init__(sys.argv)
        self.font_factor = self.calculate_font_factor(tree)
        self._font = QFont(FONT_FAMILY)
        self._font.setPointSize(self.font_factor)  # Increase font size
        self.setFont(self._font)

        self.main_window = MainWindow(tree)
        self.main_window.show()

    def run(self):
        try:
            self.exec()
        except Exception as e:
            print(e)

class MainWindow(QMainWindow):
    
    def __init__(self,tree:ET.Element):
        super().__init__()
        widget_builder = ControllerListFactory(tree)
        self.logger = logging.getLogger("MainWindow")
        self.focus_controller = FocusController(self)
        self.tree:ET.Element = tree
        
        if Config.DEBUG == "True":
            self.controller_list = widget_builder.build_widget_list(self,ControllerListFactory.TEST_LIST)
        else:
            self.controller_list = widget_builder.build_widget_list(self,ControllerListFactory.SYSTEM_SPEC_GATHERING_LIST)
        
        
        self.controller_list_index = -1
        self.current_controller:ITADController = None
        
        self.next_widget()
    
    def switch_widget(self,direction:int=1):

        if direction not in [-1,1]:
            self.logger.warning("switch widget recived unexpected input direction: {}".format(direction))
            return
        
        if self.current_controller:
            no_errors = self.current_controller.verify()
            if not no_errors:
                return

        last_view:ITADView = self.takeCentralWidget() #removes centralWidget without destorying it
        if last_view:
            last_view.has_been_viewed = True
        
        self.controller_list_index += direction
        if self.controller_list_index < 0 or self.controller_list_index > len(self.controller_list):
            self.controller_list_index -= direction
            #self.logger.warning("widget_index out of bounds")
            return
        
        self.current_controller = self.controller_list[self.controller_list_index]
        
        if not self.should_show_current_widget():
            self.switch_widget(direction)
            return
        
        if hasattr(self.current_controller,"pre_display_update"):
            self.current_controller.pre_display_update(self)
    
        self.setCentralWidget(self.current_controller.view)
        self.adjustSize()
        self.focus_controller.set_focus(self.current_controller,direction)

        if isinstance(self.centralWidget(),ExitWindow):
            self.logger.info("centralWidget is ExitWindow ... Exiting")
            print("Quitting")
            QCoreApplication.instance().quit()
        
    def previous_widget(self):
        self.switch_widget(-1)

    def next_widget(self):
        self.switch_widget()
        
    def should_show_current_widget(self) -> bool:
        """
        Returns if we should display this widget, true=display, false=dont display
        """

        return WidgetConditionProcessor.process(self.current_controller,self.tree)


    def should_next(self,event:QKeyEvent):
        return (event.key() == Qt.Key_Return 
                or event.key() == Qt.Key_Enter 
                or (event.key() == Qt.Key_Right and event.modifiers() == Qt.ShiftModifier)
                )

    def should_back(self,event:QKeyEvent):
        return (event.key() == Qt.Key_Backspace 
            or (event.key() == Qt.Key_Left and event.modifiers() == Qt.ShiftModifier )
            )

    def keyPressEvent(self, event:QKeyEvent):
        if self.should_next(event):
            self.next_widget()

        elif self.should_back(event):
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
        #self.current_controller.adjustSize()


class FocusController():
    def __init__(self,parent:QMainWindow):
        self.parent = parent
    
    def set_focus(self,controller:ITADController,direction:int):

        object_Of_Focus = controller.findChild(QObject,"Object_Of_Focus")

        if not object_Of_Focus:
            #If no Object_Of_Focus
            if not controller.view.has_been_viewed or isinstance(controller,(BasicListController)):
                controller.setFocus()
        elif direction == 1:
            #Going forward we only set focus if its a never before seen widget
            if not controller.view.has_been_viewed or isinstance(object_Of_Focus,(QListWidget)):
                object_Of_Focus.setFocus()
        else:
            #going backward we only set focus if the object is a listwidget
            if isinstance(object_Of_Focus,(QListWidget)):
                object_Of_Focus.setFocus()
