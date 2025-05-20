
from Generics import ITADController
from HardwareTests.Views.KeyboardTestView import KeyboardTestView
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt

class KeyboardTestController(ITADController):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.view:KeyboardTestView
    
    def connect_view(self, view:KeyboardTestView):
        super().connect_view(view)
        self.view.keyPressEvent = self.key_pressed
        self.view.keyReleaseEvent = self.key_release
        self.view.next_widget_btn.pressed.connect(lambda: self.parent.switch_widget(1))
        self.view.prev_widget_btn.pressed.connect(lambda: self.parent.switch_widget(-1))
    

    scan_codes = {
        65513:"L-Alt",
        65514:"R-Alt",
        65505:"L-Shift",
        65506:"R-Shift",
        65507:"L-Ctrl",
        65508:"R-Ctrl",
    }

    def get_key(self,event:QKeyEvent):
        key = event.key()
        if(event.nativeVirtualKey() in self.scan_codes):
            key = self.scan_codes[event.nativeVirtualKey()]
        return key

    def key_release(self, event:QKeyEvent):
        key = self.get_key(event)
        self.view.keyboard.release_key(key)

    def key_pressed(self, event:QKeyEvent):
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.parent.keyPressEvent(event)
        
        key = self.get_key(event)

        self.view.keyboard.press_key(key)
        