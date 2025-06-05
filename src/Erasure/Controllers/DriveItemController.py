from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt,pyqtSlot

import xml.etree.ElementTree as ET
from Erasure.Services.WiperServices import WipeService
from Erasure.Services.ErasureTimeService import TimeService
from Erasure.Views.DriveItemView import DriveItemView
from Erasure.Controllers.DriveModel import DriveModel
from Erasure.Services.DriveServices import DriveService

from Erasure.Messages import *

class DriveController(QObject):
    #statusChanged = pyqtSignal(Message)
    adjustSize = pyqtSignal()
    
    def __init__(self,drive_model:'DriveModel'):
        super().__init__()
        self.drive_model = drive_model
        self.drive_service = DriveService(self.drive_model)
        self.view = None  # Will be set when connecting to view
        self.wipe_method = None 

    def connect_to_view(self,view:DriveItemView):
        self.view = view
        self.view.setObjectName("drive_item_view")
        self.view.wipe_button.pressed.connect(self.handle_wipe_request)

        self.time_service = TimeService()
        self.time_service.connect_to_view(self.view.status_box)
    
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
        self.wipe_service = WipeService(self.drive_model,method)
        self.wipe_service.exception.connect(self.handle_error)
        self.wipe_service.update.connect(self.slot_handle_erasure_messages)
        self.wipe_service.start_wipe()
    
    def select_drive(self,selected:bool):
        self.view.set_checked(selected)
    
    def should_wipe(self):
        selected = self.view.wipe_checkbox.isChecked()
        removeable = self.drive_model.removeable
        return selected or removeable

    def confirm_wipe(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Wipe Drive")
        msg_box.setText(f"Are you sure you want to wipe '{self.drive_model.name}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes

    @pyqtSlot(Message)
    def slot_handle_erasure_messages(self,message:Message):

        acceptable_messages = [ErasureTimeUpdateMessage,
                               ErasureStatusUpdateMessage,StartErasureMessage,ErasureErrorMessage,ErasureSuccessMessage
                               ]
        if message.__class__ not in acceptable_messages:
            print("Illegal message passed to DriveController: {}".format(message))
            return
        if isinstance(message,StartErasureMessage):
            self.drive_model.wipe_started = datetime.now()
            self.time_service.start_timer()

        if isinstance(message,ErasureStatusUpdateMessage):
            self.view.status_label.update_status(message.message)
            self.time_service.find_percentage(message)
            self.view.setStyleSheet(message.stylesheet)

        if isinstance(message,ErasureSuccessMessage):
            self.drive_model.wipe_success = True
        
        self.time_service.update_timer()

        


        self.adjustSize.emit()

    def handle_error(self,error_msg):
        self.slot_handle_erasure_messages(ErasureErrorMessage("Pythonic error in the thread"))
        
        QMessageBox.warning(
            self.view, "Wipe Error", 
            f"Error wiping drive '{self.drive_model.name}': {error_msg}"
        )

