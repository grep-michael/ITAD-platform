from PyQt5.QtWidgets import *
from GUIs.CustomWidgets import *
from Erasure.Drives import *
import xml.etree.ElementTree as ET


COLUMNS = 3


class ErasureWindowView(QWidget):
    """
    Main window for the erasure application.
    """
    
    def __init__(self):
        super().__init__()
        self.setObjectName("erasure_window")
        self.drive_views = []
        self.initUI()
        #self.set_controls_view()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)

        self.controls_view = ErasureControlsView()
        #self.controls_view = 

        self.grid_layout = QGridLayout()
        self.grid_container = QWidget()

        self.grid_container.setLayout(self.grid_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.grid_container)
        
        # Add layouts to main layout
        self.main_layout.addLayout(self.controls_view)
        self.main_layout.addWidget(self.scroll_area)
        
        self.setLayout(self.main_layout)
    
    def add_drive_view(self,drive_view):
        self.drive_views.append(drive_view)
        self.update_grid()

    def set_controls_view(self):

        while self.controls_container.count():
            item = self.controls_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        controls_view = ErasureControlsView()

        self.controls_view = controls_view
        self.controls_container.addWidget(controls_view)

    def update_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                self.grid_layout.removeWidget(item.widget())
        
        for i, drive_view in enumerate(self.drive_views):
            
            row = i // COLUMNS
            col = i % COLUMNS
            self.grid_layout.addWidget(drive_view, row, col, alignment=Qt.AlignCenter)

    def sizeHint(self):
        # Return the natural size of the content
        if hasattr(self, 'grid_container'):
            content_size = self.grid_container.sizeHint()
            # Add margins for scroll bars if needed
            scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            return QSize(content_size.width() + scrollbar_width, self.height())
        return super().sizeHint()

class ErasureControlsView(QVBoxLayout):

    def __init__(self):
        super().__init__()
        self.create_controls_layout()
    
    def create_controls_layout(self):
        button_layout = QHBoxLayout()
        button_layout.setObjectName("controls_hbox")

        self.eraseAllButton = QPushButton("Erase All")
        self.selectAllButton = QPushButton("Select All")
        self.unselectAllButton = QPushButton("Unselect All")
        self.eraseSelectedButton = QPushButton("Erase Selected")

        button_layout.addWidget(self.eraseAllButton)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.unselectAllButton)
        button_layout.addWidget(self.eraseSelectedButton)

        
        erasure_methods = {
            "Default":WipeMethod,
            "Partition Header Erasure":PartitionHeaderErasure,
            "NVMe Secure Erase":NVMeSecureErase,
            "RandomOverwrite":RandomOverwrite,
            "Fake Erasure":FakeWipe
        }

        self.method_selector = QComboBox()
        self.method_selector.setObjectName("method_selector")
        for method, _class in erasure_methods.items():
            self.method_selector.addItem(method,_class)

        #vbox = QVBoxLayout()
        self.addLayout(button_layout)
        self.addWidget(self.method_selector)
        #self.setLayout(vbox)

class ErasureController(QObject):
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
            controller.initiate_wipe(self.get_current_method())

    def on_method_changed(self):
        method_class = self.view.controls_view.method_selector.currentData()
        print(method_class)
        self.selected_method = method_class

    def confirm_bulk_erase(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Erase Drives")
        msg_box.setText("Are you sure you want to erase the selected drives?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes

    def load_drive_models(self,drive_models:list[DriveModel]):
        
        # Clear existing controllers
        for controller in self.drive_controllers.values():
            controller.deleteLater()
        self.drive_controllers.clear()
        
        # Create drive views and controllers
        for drive_model in drive_models:
            drive_view = DriveItemView(drive_model)
            self.view.add_drive_view(drive_view)
            
            # Create and connect controller
            controller = DriveController(drive_model )#self.wipe_method_factory)
            controller.connect_to_view(drive_view)
            self.drive_controllers[drive_model.name] = controller
    
class ErasureApp(QFrame):

    def __init__(self, tree:ET.Element):
        super().__init__()
        layout = QVBoxLayout()
        window = self.create_main_window()
        layout.addWidget(window)
        self.setLayout(layout)
        self.load_drives(tree)
        

    def create_main_window(self):
        main_window = ErasureWindowView()
        self.erasure_controller = ErasureController()
        self.erasure_controller.connect_to_view(main_window)
        return main_window

    def load_drives(self,xml_tree):
        drives = self.create_drive_models(xml_tree)
        self.erasure_controller.load_drive_models(drives)

    def create_drive_models(self, xml_tree):
        drive_models = []
        storage_elements = xml_tree.findall(".//SYSTEM_INVENTORY/Devices/Storage")
        
        for storage_xml in storage_elements:
            drive_model = DriveModel(storage_xml)
            drive_models.append(drive_model)
            
        return drive_models


