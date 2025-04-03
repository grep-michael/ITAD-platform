from PyQt5.QtWidgets import *
from GUIs.CustomWidgets import *
from Erasure.Services.ErasureProcesses import *
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
            "Default":None,
            "Partition Header Erasure":PartitionHeaderErasureProcess,
            "NVMe Secure Erase":NVMeSecureEraseProcess,
            "RandomOverwrite":RandomOverwriteProcess,
            #"Fake Erasure":FakeWipe
        }
        self.method_selector = QComboBox()
        self.method_selector.setObjectName("method_selector")
        for method, _class in erasure_methods.items():
            self.method_selector.addItem(method,_class)
        #vbox = QVBoxLayout()
        self.addLayout(button_layout)
        self.addWidget(self.method_selector)
        #self.setLayout(vbox)
