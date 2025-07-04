from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeyEvent
import math
from Erasure.Controllers.DriveItemController import *
import xml.etree.ElementTree as ET
from Erasure.Views.ErasureWindowView import ErasureWindowView 
from Generics import ITADController


class ErasureWindowController(ITADController):

    def __init__(self,parent):
        super().__init__()
        self._parent:QWidget = parent
        self.drive_controllers:dict[str,DriveController] = {}  
        self.selected_method = None
        self.hotplug_override = False

    def connect_view(self,view:ErasureWindowView):
        self.view:ErasureWindowView = view
        self.view._parent = self._parent

        self.view.keyPressEvent = self.key_pressed


        self.view.show_event.connect(self.handle_show_event)
        self.load_drive_models()

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)

        self.view.controls_view.eraseAllButton.clicked.connect(self.wipe_all)
        self.view.controls_view.selectAllButton.clicked.connect(self.select_all)
        self.view.controls_view.unselectAllButton.clicked.connect(self.unselect_all)
        self.view.controls_view.eraseSelectedButton.clicked.connect(self.wipe_selected)

        self.view.controls_view.method_selector.currentIndexChanged.connect(self.on_method_changed)
    
    def key_pressed(self, event:QKeyEvent):
        if event.modifiers() == Qt.ShiftModifier and (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) :
            self._parent.keyPressEvent(event)

    def wipe_all(self):
        self.select_all()
        self.wipe_selected()

    def select_all(self):
        for controller in self.drive_controllers.values():
            controller.select_drive(True)

    def unselect_all(self):
        for controller in self.drive_controllers.values():
            controller.select_drive(False)

    def get_wipe_method(self):
        return self.selected_method
    
    def wipe_selected(self):
        selected_controllers = [
            i for i in self.drive_controllers.values() if i.should_wipe()
        ]

        if not selected_controllers:
            QMessageBox.information(
                self.view, "No Drives Selected", 
                "Please select at least one drive to erase."
            )
            return
        if not self.confirm_bulk_erase():
            return
        
        for controller in selected_controllers:
            controller.wipe(self.get_wipe_method())

    def on_method_changed(self):
        method_class = self.view.controls_view.method_selector.currentData()
        self.selected_method = method_class
        for controller in self.drive_controllers.values():
            controller.change_method(method_class)

    def confirm_bulk_erase(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Erase Drives")
        msg_box.setText("Are you sure you want to erase the selected drives?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        return msg_box.exec() == QMessageBox.Yes

    @pyqtSlot()
    def handle_show_event(self):
        self.wipe_all()

    @pyqtSlot()
    def slot_adjust_size(self):
        self.view.adjustSize()
        if not self._parent.isMaximized():
            self.set_view_geometry()
            self._parent.resize(self.view.width(),self.view.height())

    def pre_display_update(self,parent:QMainWindow):
        drive_count = 0
        removeable_count = 0

        for i in self.drive_controllers.values():
            if i.drive_model.removeable:
                removeable_count += 1
            else:
                drive_count += 1

        header = "Drives: {}   HotPlugs: {}".format(drive_count,removeable_count)
        self._parent.setWindowTitle(header)

        self.set_view_geometry()

    def set_view_geometry(self):
        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height()# - 100
        screen_width = desktop.availableGeometry().width()# - 50

        prefered_height = min(self.view.sizeHint().height(),screen_height)
        prefered_width = min(self.view.sizeHint().width(),screen_width)
        self.view.setMinimumHeight(prefered_height)
        self.view.setMinimumWidth(prefered_width)
        self.view.adjustSize()

    def create_drive_models(self, xml_tree:ET.Element):
        drive_models = []
        storage_elements = xml_tree.findall(".//SYSTEM_INVENTORY/Devices/Storage")
        
        for storage_xml in storage_elements:
            drive_model = DriveModel(storage_xml)
            drive_models.append(drive_model)
            
        self.drive_models:list[DriveModel] = drive_models

    def load_drive_models(self):
        # Clear existing controllers
        for controller in self.drive_controllers.values():
            controller.deleteLater()
        self.drive_controllers.clear()
        
        self.columns = max(min(len(self.drive_models),4),1)
        max_width = math.floor(QDesktopWidget().availableGeometry().width()/ self.columns ) - 50 #padding
        
        # Create drive views and controllers
        for drive_model in self.drive_models:
            if drive_model.has_removed_tag():
                continue
            drive_view = DriveItemView(drive_model,self.view)
            drive_view.setMaximumWidth(max_width)
            
            # Create and connect controller
            controller = DriveController(drive_model)
            controller.connect_to_view(drive_view)
            controller.adjustSize.connect(self.slot_adjust_size)

            self.drive_controllers[drive_model.serial] = controller
        self.add_drives_to_view()

    def add_drives_to_view(self):
        self.view.clear_drive_view_list()
        self.view.clear_grid()
    
        for controller in self.drive_controllers.values():
            if not controller.drive_model.removeable or self.hotplug_override:
                self.view.add_drive_view(controller.view)
                controller.view.show()
            else:
                controller.view.hide()
        self.view.update_grid(self.columns)
        self.slot_adjust_size()


    def show_context_menu(self, position):
        """Show context menu at the given position"""
        # Create the context menu
        context_menu = QMenu(self.view)

        # Add a header action (disabled, just for display)
        toggle_action = QAction("toggle hidden", self)
        toggle_action.setEnabled(True)
        context_menu.addAction(toggle_action)
        context_menu.addSeparator()

        #toggle_action.setCheckable(True)
        #toggle_action.setChecked(False)
        toggle_action.triggered.connect(self.toggle_hotplug_drives)
        

        # Show the context menu at the cursor position
        context_menu.exec_(self.view.mapToGlobal(position))

    def toggle_hotplug_drives(self):
        self.hotplug_override = not self.hotplug_override
        self.add_drives_to_view()

    def verify(self):
        for controller in self.drive_controllers.values():
            if not controller.should_pass_verify():
                return False
        return True

