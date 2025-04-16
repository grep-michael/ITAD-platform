from Views.BasicNodeView import BasicNodeView
from PyQt5.QtGui import QFontMetrics,QPixmap
from PyQt5.QtWidgets import *

class WebCamView(BasicNodeView):
    def __init__(self):
        super().__init__()
        self.build_png()

    def build_png(self):
        try:
            pixmap = QPixmap("specs/webcam.png")
            image_label = QLabel("Webcam png")
            image_label.setPixmap(pixmap)
            self.vbox.addWidget(image_label)
        except Exception as e:
            #no webcam
            print(e)