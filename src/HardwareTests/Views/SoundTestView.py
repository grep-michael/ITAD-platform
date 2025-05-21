from Generics import ITADView
from PyQt5.QtWidgets import *

class SoundTestView(ITADView):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        vbox = QVBoxLayout()
        self.play_button = QPushButton("Play Sound")
        label = QLabel("Give it 1 second for the audio service to start")

        vbox.addWidget(label)
        vbox.addWidget(self.play_button)

        self.setLayout(vbox)