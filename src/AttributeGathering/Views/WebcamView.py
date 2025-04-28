from AttributeGathering.Views.BasicNodeView import BasicNodeView
from PyQt5.QtGui import QFontMetrics,QPixmap
from PyQt5.QtWidgets import *

class WebCamView(BasicNodeView):
    def __init__(self):
        super().__init__()
        
    def build_from_element(self, element):
        super().build_from_element(element)
        self.build_controls()
        self.build_png()

    def build_controls(self):
        self.controls = QHBoxLayout()
        
        self.video_selector = QComboBox()
        self.controls.addWidget(self.video_selector)

        self.retake_button = QPushButton("Retake picture")
        self.controls.addWidget(self.retake_button)

        self.vbox.addLayout(self.controls)

    def update_png(self):
        print("update_png")
        self.pixmap.load("specs/webcam.png")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.update()

    def build_png(self):
        self.pixmap = QPixmap("specs/webcam.png")
        self.image_label = QLabel("Webcam png")
        self.image_label.setPixmap(self.pixmap)
        self.vbox.addWidget(self.image_label)
        #try:
        #    self.pixmap = QPixmap("specs/webcam.png")
        #    self.image_label = QLabel("Webcam png")
        #    self.image_label.setPixmap(self.pixmap)
        #    self.vbox.addWidget(self.image_label)
        #except Exception as e:
        #    #no webcam
        #    print(e)