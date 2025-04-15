from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from GUIs.CustomWidgets import *
from Erasure.Controllers.DriveItemController import *
import xml.etree.ElementTree as ET
from Erasure.Views.ErasureWindowView import ErasureWindowView 


class ErasureController(QObject):
    adjustSize = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.wipe_method_factory = wipe_method_factory
        #self.logger_service = logger_service
        self.drive_controllers:dict[str,DriveController] = {}  
        self.selected_method = None

    def connect_to_view(self,view:ErasureWindowView):
        self.view:ErasureWindowView = view

        self.view.controls_view.eraseAllButton.clicked.connect(self.wipe_all)
        self.view.controls_view.selectAllButton.clicked.connect(self.select_all)
        self.view.controls_view.unselectAllButton.clicked.connect(self.unselect_all)
        self.view.controls_view.eraseSelectedButton.clicked.connect(self.wipe_selected)

        self.view.controls_view.method_selector.currentIndexChanged.connect(self.on_method_changed)
    
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
            i for i in self.drive_controllers.values() if i.isSelected()
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
    def slot_adjust_size(self):
        self.view.adjustSize()
        self.adjustSize.emit()

    def load_drive_models(self,drive_models:list[DriveModel]):
        
        # Clear existing controllers
        for controller in self.drive_controllers.values():
            controller.deleteLater()
        self.drive_controllers.clear()
        
        # Create drive views and controllers
        for drive_model in drive_models:
            if drive_model.is_removed():
                continue
            drive_view = DriveItemView(drive_model,self.view)
            self.view.add_drive_view(drive_view)
            
            # Create and connect controller
            controller = DriveController(drive_model)#self.wipe_method_factory)
            controller.connect_to_view(drive_view)
            controller.adjustSize.connect(self.slot_adjust_size)
            self.drive_controllers[drive_model.name] = controller
    