
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

    def key_pressed(self, event:QKeyEvent):
        key = event.key()
        if key == Qt.Key_Left or key == Qt.Key_Right:
            self.parent.keyPressEvent(event)

        if(event.nativeVirtualKey() in self.scan_codes):
            key = self.scan_codes[event.nativeVirtualKey()]

        self.view.keyboard.press_key(key)
        