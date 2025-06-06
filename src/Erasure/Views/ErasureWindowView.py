from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QSize,pyqtSignal
from Erasure.Services.ErasureProcesses import *
import xml.etree.ElementTree as ET
from Generics import ITADView




class ErasureWindowView(ITADView):
    """
    Main window for the erasure application.
    """

    show_event = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._parent:QWidget
        self.setObjectName("erasure_window")
        self.drive_views = []
        self.initUI()
        #self.set_controls_view()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        self.controls_view = ErasureControlsView()
        #self.controls_view = 

        self.grid_layout = QGridLayout()

        self.grid_container = QWidget()
        self.grid_container.setObjectName("grid_container")
        self.grid_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
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
        #self.update_grid()

    def update_grid(self,COLUMNS=3):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                self.grid_layout.removeWidget(item.widget())
        
        for i, drive_view in enumerate(self.drive_views):
            row = i // COLUMNS
            col = i % COLUMNS
            self.grid_layout.addWidget(drive_view, row, col, alignment=Qt.AlignCenter)
        self.adjustSize()
        self._parent.adjustSize()

    def adjustSize(self):
        if not self._parent.isMaximized():
            super().adjustSize()
            #self._parent.adjustSize()
        return 

    def showEvent(self,event):
        self.show_event.emit()
        super().showEvent(event)

    def sizeHint(self):
        if hasattr(self, 'grid_container') and not self._parent.isMaximized():
            #if the window is maximized we dont have to worry about filling space as we literally have max space to work with
            grid_size = self.grid_container.sizeHint()
            control_size = self.controls_view.sizeHint()
            
            min_width = max(grid_size,control_size,key=lambda obj: obj.width())
            scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            
            combined = control_size.height() + grid_size.height()
            #the 100 and 100 here are arbitrary, sizing just sucks on computers so we make sure theres alot of room
            height = min(QDesktopWidget().availableGeometry().height()-100,combined+100)

            return QSize(min_width.width() + scrollbar_width + 30,
                         height)
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
        
        erasure_methods = self.get_all_easure_process()

        self.method_selector = QComboBox()
        self.method_selector.setObjectName("method_selector")
        for method, _class in erasure_methods.items():
            self.method_selector.addItem(method,_class)
        #vbox = QVBoxLayout()
        self.addLayout(button_layout)
        self.addWidget(self.method_selector)
        #self.setLayout(vbox)

    def get_all_easure_process(self)->dict[str,ErasureProcess]:
        subclasses:list[ErasureProcess] = set(ErasureProcess.__subclasses__())
        cd = {
            "Default":ErasureProcess
        }
        for _class in subclasses:
            cd[_class.DISPLAY_NAME] = _class
        return cd