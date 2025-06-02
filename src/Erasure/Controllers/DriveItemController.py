from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt
import xml.etree.ElementTree as ET
from Erasure.Services.WiperServices import WipeService
from Erasure.Views.DriveItemView import DriveItemView
from Erasure.Controllers.DriveModel import DriveModel
from Erasure.Services.DriveServices import DriveService


class DriveController(QObject):
    statusChanged = pyqtSignal(str, str, bool)
    adjustSize = pyqtSignal()
    
    def __init__(self,drive_model:'DriveModel'):
        super().__init__()
        self.drive_model = drive_model
        self.drive_service = DriveService(self.drive_model)
        self.view = None  # Will be set when connecting to view
        self.wipe_method = None 

    def connect_to_view(self,view:DriveItemView):
        self.view = view
        self.view.wipe_button.pressed.connect(self.handle_wipe_request)
        self.statusChanged.connect(self.view.slot_status_update)
    
    def handle_wipe_request(self):
        """
        Handle Wipe request from the view
        """
        if self.confirm_wipe():
            self.wipe(self.wipe_method)

    def change_method(self,method):
        self.wipe_method = method

    def wipe(self,method):
        """
        handles wiping, called directly from the erasurewindow controller
        """
        if not self.drive_service.is_disk_present():
            self.emit_status_signal("Drive not present")
            self.drive_service.set_removed()
            return
        self.emit_status_signal("wiping")
        self.wipe_service = WipeService(self.drive_model,method)
        self.wipe_service.exception.connect(self.handle_error)
        self.wipe_service.update.connect(self.emit_status_signal) #TODO hook other singals
        self.wipe_service.start_wipe()
    
    def select_drive(self,selected:bool):
        self.view.set_checked(selected)
    
    def isSelected(self):
        return self.view.wipe_checkbox.isChecked()

    def confirm_wipe(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Wipe Drive")
        msg_box.setText(f"Are you sure you want to wipe '{self.drive_model.name}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes

    def emit_status_signal(self,message:str,style:str="",override:bool=False):
        self.statusChanged.emit(message, style, override)
        self.adjustSize.emit()
    
    def handle_error(self,error_msg):
        self.emit_status_signal("Error")
        QMessageBox.warning(
            self.view, "Wipe Error", 
            f"Error wiping drive '{self.drive_model.name}': {error_msg}"
        )

