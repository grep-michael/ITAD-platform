
from Generics import ITADController
from HardwareTests.Views.KeyboardTestView import KeyboardTestView

class KeyboardTestController(ITADController):
    def __init__(self):
        super().__init__()
    
    def connect_view(self, view:KeyboardTestView):
        super().connect_view(view)
        #test file 