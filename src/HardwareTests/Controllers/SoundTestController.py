from Generics import ITADController
from PyQt5.QtWidgets import *

from HardwareTests.Views.SoundTestView import SoundTestView
from HardwareTests.Services.SoundTestService import SoundTestService

class SoundTestController(ITADController):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self.sound_service = SoundTestService()
    
    def connect_view(self, view:SoundTestView):
        self.view:SoundTestView = view
        self.view.play_button.pressed.connect(self.play_sound)
        self.view.good_button.pressed.connect(self.mark_good)
        self.view.bad_button.pressed.connect(self.mark_bad)

    def mark_good(self):
        self.view.bad_button.setStyleSheet("")
        self.element.text = "Audio Diagnostics: Passed"
        self.view.good_button.setStyleSheet("background-color: #C6F6C6;")
        
    def mark_bad(self):
        self.view.good_button.setStyleSheet("")
        self.element.text = "Audio Diagnostics: Failed"
        self.view.bad_button.setStyleSheet("background-color: #C6F6C6;")

    def play_sound(self):
        self.sound_service.beep()
    
