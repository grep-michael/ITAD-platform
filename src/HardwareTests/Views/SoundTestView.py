from Generics import ITADView
from PyQt5.QtWidgets import *

class SoundTestView(ITADView):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        vbox = QVBoxLayout()

        label = QLabel("Give it 1 second for the audio service to start")
        vbox.addWidget(label)

        vbox.addLayout(self.build_play_button())

        vbox.addLayout(self.build_result_buttons())

        self.setLayout(vbox)
    
    def build_play_button(self):
        box = QHBoxLayout()
        self.play_button = QPushButton("Play Sound")
        box.addWidget(self.play_button)
        return box

    def build_result_buttons(self):
        box = QHBoxLayout()

        self.good_button = QPushButton("Mark as good")
        box.addWidget(self.good_button)

        self.bad_button = QPushButton("Mark as bad")
        box.addWidget(self.bad_button)
        return box