from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys,subprocess,re
import xml.etree.ElementTree as ET
from GUIs.CustomWidgets import ITADWidget
from collections import defaultdict
#from Wiper import *
from DiskErasure import *

class DriveWidget(QFrame):
    def __init__(self,storage_xml:ET):
        """
        Args:
            storage_xml (ET.Element) -> storage xml of storage device
        """
        super().__init__()
        self.xml = storage_xml
        self.friendly_name = storage_xml.find(".//Name").text
        
        
        self.setStyleSheet("DriveWidget { border: 2px solid black; } ")
        self.build_matser_layout()

        #self.setStyleSheet("border: 2px solid black; background-color: red;")

    def build_matser_layout(self):
        master_layout = QVBoxLayout()
        controls = self.build_controls()
        info_box = self.build_info_box(self.xml)
        status = self.build_status()

        master_layout.addLayout(controls)
        master_layout.addLayout(info_box)
        master_layout.addLayout(status)

        self.setLayout(master_layout)

    def build_controls(self):
        hbox = QHBoxLayout()
        label = QLabel("Selected:")
        self.wipe_checkbox = QCheckBox()
        self.wipe_checkbox.setObjectName("wipe_check_box")
        self.wipe_button = QPushButton(text="Wipe")
        self.wipe_button.clicked.connect(self._self_wipe)
        hbox.addWidget(label,alignment=Qt.AlignRight)
        hbox.addWidget(self.wipe_checkbox,alignment=Qt.AlignLeft)
        hbox.addWidget(self.wipe_button)

        return hbox

    def build_info_box(self,xml:ET):
        fields = ["Name","Model","Serial_Number","Size"]        
        vbox = QVBoxLayout()
        
        for field in fields:
            value = xml.find(".//{}".format(field)).text
            vbox.addWidget(QLabel(value))
        
        return vbox

    def build_status(self):
        vbox = QVBoxLayout()
        self.status_label = QLabel("Status")
        removed = self.xml.find("Removed")
        if removed is not None:
            self.status_label.setText("Removed")
            self.status_label.setStyleSheet("color: red;")
        self.status_label.setObjectName("Status_box")
        vbox.addWidget(self.status_label)
        return vbox
    
    def _self_wipe(self):
        self.parent().showMaximized()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Wipe?")
        msg_box.setText("Confirm Wipe")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg_box.exec()
        if result == QMessageBox.Yes:
            self.wipe_checkbox.setChecked(True)
            self.wipe()

    def get_selected_method(self) -> callable:
        def find_parent(widget,target_name):
            parent = widget.parent()
            if parent is None:
                return None
            if parent.objectName() == target_name:
                return parent
            return find_parent(parent, target_name)

        main_parent = find_parent(self,"erasure_window")
        method_box = main_parent.findChild(QComboBox,"erasure_methods_box")
        return method_box.currentData()

    def wipe(self):
        checkbox = self.findChild(QCheckBox, "wipe_check_box")
        if checkbox.isChecked():
            
            if not hasattr(self,"wipe_thread") or self.wipe_thread.isFinished(): #ensures a wipe wont run while a wipe is still running
                #self.drive = Drive(self.xml)
                method = self.get_selected_method()

                self.drive = WipeObserver(self.xml)
                self.drive.set_method(method)

                self.wipe_thread = QThread()
                obj = self.drive
                obj.moveToThread(self.wipe_thread)
                
                obj.update.connect(self.onUpdate)
                obj.exception.connect(self.onException)
                obj.finished.connect(self.finish_wipe)

                self.wipe_thread.started.connect(obj.run_method_deterministic)
                
                self.wipe_thread.start()

    def finish_wipe(self):
        print("thread finished: {}".format(self.friendly_name))
        self.drive.deleteLater()
        self.wipe_thread.quit()
        self.wipe_thread.wait()

    def onException(self, msg):
        QMessageBox.warning(self,"Excpetion in wiper thread: ",msg)

    def onUpdate(self, status_msg,stylesheet,override):
        label = self.findChild(QLabel, "Status_box")
        if not override:
            stylesheet = self.styleSheet()+stylesheet
        self.setStyleSheet(stylesheet)
        label.setText("{}".format(status_msg))

    def update_status(self,status:str):
        self.status_label.setText(status)

COLUMNS = 3

class ErasureWindow(ITADWidget):

    def __init__(self, tree):
        super().__init__()
        self.tree = tree
    
    def pre_display_update(self,parent):
        self.storages = self.build_storage_list(self.tree)
        self.setObjectName("erasure_window")
        self.build_master_layout()

        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height() - 100
        prefered_height = min(self.grid_container.height(),screen_height)
        self.setFixedHeight(prefered_height)

    def build_master_layout(self):

        main_layout = QVBoxLayout(self)
        main_layout.setObjectName("main_layout")
        main_layout.setContentsMargins(0, 0, 0, 0)

        controls = self.build_controls()

        self.grid_container = QWidget()
        self.grid_container.setObjectName("grid_container")
        self.grid_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.grid_container.setLayout(self.build_grid(self.storages))

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.grid_container)

        main_layout.addLayout(controls)
        main_layout.addWidget(self.scroll)

        self.setLayout(main_layout)

    def sizeHint(self):
        # Return the natural size of the content
        if hasattr(self, 'grid_container'):
            content_size = self.grid_container.sizeHint()
            # Add margins for scroll bars if needed
            scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            return QSize(content_size.width() + scrollbar_width, self.height())
        return super().sizeHint()

    def wipe_all(self):
        self._set_all_checkboxes(True)
        self.wipe_checked()

    def _set_all_checkboxes(self, state):
        check_boxes = self.findChildren(QCheckBox, "wipe_check_box")
        for box in check_boxes:
            box.setChecked(state)

    def _loop_over_drives_and_wipe(self):
        self.showMaximized()
        self.parent().showMaximized()
        drives = self.findChildren(DriveWidget)
        for drive in drives:
            drive.wipe()

    def comfirm_erasure(self) -> bool:
        """
        True if user selected yes, false if user elect wipe
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Erase?")
        msg_box.setText("Confirm Erase")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(msg_box.button(QMessageBox.Yes))
        result = msg_box.exec()
        return result == QMessageBox.Yes

    def wipe_checked(self):
        if self.comfirm_erasure():
            self._loop_over_drives_and_wipe()
        
    def build_controls(self):
        controls = QHBoxLayout()
        controls.setObjectName("controls_hbox")
        buttons = {
            "Erase All": self.wipe_all,
            "Select All":lambda: self._set_all_checkboxes(True),
            "Unselect All":lambda: self._set_all_checkboxes(False),
            "Erase Selected":self.wipe_checked,
        }
        for key,value in buttons.items():
                button = QPushButton(text=key)
                button.setMinimumWidth(QFontMetrics(button.font()).width("Erase Selected")+7) #Erase Selected is the longest string so we use it to set the min width
                button.clicked.connect(value)
                controls.addWidget(button)
        
        erasure_methods = {
            "Default":WipeMethod,
            "Partition Header Erasure":PartitionHeaderErasure,
            "NVMe Secure Erase":NVMeSecureErase,
            "RandomOverwrite":RandomOverwrite,
            "Fake Erasure":FakeWipe
        }

        erasure_methods_widget = QComboBox()
        erasure_methods_widget.setObjectName("erasure_methods_box")
        for method, _class in erasure_methods.items():
            erasure_methods_widget.addItem(method,_class)

        vbox = QVBoxLayout()
        vbox.addLayout(controls)
        vbox.addWidget(erasure_methods_widget)

        return vbox

    def build_grid(self,storage_list):
        layout = QGridLayout(self)
        layout.setObjectName("grid_layout")
        order_index = 0
        row = 0
        while 1:
            for c in range(COLUMNS):
                layout.addWidget(storage_list[order_index],row,c,alignment=Qt.AlignCenter)
                order_index+=1
                if order_index > len(storage_list)-1:
                    break
            row +=1
            if order_index > len(storage_list)-1:
                break
        
        return layout

    def build_storage_list(self,tree):
        storages = tree.findall(".//SYSTEM_INVENTORY/Devices/Storage")
        storage_list = []
        for storage in storages:            
            storage_list.append(DriveWidget(storage))
        return storage_list

    def showEvent(self,event):
        super().showEvent(event)
        self.wipe_all()

    def verify(self):
        return True