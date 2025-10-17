from Generics import ITADController
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
        self.element.text = "Audio Diagnostics: Passed"
    def mark_bad(self):
        self.element.text = "Audio Diagnostics: Failed"

    def play_sound(self):
        self.sound_service.beep()
    
