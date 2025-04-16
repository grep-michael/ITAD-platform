from Generics import ITADWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QSize

COLUMNS = 3

class OverviewView(ITADWidget):
    def __init__(self):
        super().__init__()
        self.child_views:list[QWidget] = []
        self.setObjectName("overview_window")
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        self.grid_container = QWidget()
        self.grid_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.grid_container.setLayout(self.grid_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.grid_container)

        self.main_layout.addWidget(self.scroll_area)        
        self.setLayout(self.main_layout)


    def add_view(self,view):
        self.child_views.append(view)
        self.update_grid()

    def update_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                self.grid_layout.removeWidget(item.widget())
        
        for i, view in enumerate(self.child_views):
            row = i // COLUMNS
            col = i % COLUMNS
            self.grid_layout.addWidget(view, row, col, alignment=Qt.AlignCenter)
        self.adjustSize()

    def sizeHint(self):
        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height() - 100
        prefered_height = min(self.grid_container.height(),screen_height)
        self.setFixedHeight(prefered_height)

        self.setMinimumWidth(self.grid_container.sizeHint().width()+10)
        
        if hasattr(self, 'grid_container'):
            #if the window is maximized we dont have to worry about filling space as we literally have max space to work with
            content_size = self.grid_container.sizeHint()
            scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            return QSize(content_size.width() + scrollbar_width + 30, self.height())
        return super().sizeHint()

    