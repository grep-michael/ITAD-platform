from Generics import ITADController
from HardwareTests.Views.SoundTestView import SoundTestView
from HardwareTests.Services.SoundTestService import SoundTestService

class SoundTestController(ITADController):
    def __init__(self, element):
        super().__init__()
        self.sound_service = SoundTestService()
    
    def connect_view(self, view:SoundTestView):
        self.view:SoundTestView = view
        self.view.play_button.pressed.connect(self.play_sound)

    def play_sound(self):
        self.sound_service.beep()
    
