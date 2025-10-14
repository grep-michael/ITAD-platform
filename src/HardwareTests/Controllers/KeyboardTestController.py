
from Generics import ITADController
from HardwareTests.Views.KeyboardTestView import KeyboardTestView
from PyQt5.QtGui import QKeyEvent,QKeySequence
from PyQt5.QtCore import Qt

class KeyboardTestController(ITADController):
    def __init__(self,element,parent):
        super().__init__()
        self.element = element
        self.parent = parent
        self.view:KeyboardTestView
        self.unpressed_keys = [Qt.Key_Escape, Qt.Key_Print, Qt.Key_QuoteLeft, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_0, Qt.Key_Minus, Qt.Key_Equal, Qt.Key_Backspace, Qt.Key_Tab, Qt.Key_Q, Qt.Key_W, Qt.Key_E, Qt.Key_R, Qt.Key_T, Qt.Key_Y, Qt.Key_U, Qt.Key_I, Qt.Key_O, Qt.Key_P, Qt.Key_BracketLeft, Qt.Key_BracketRight, Qt.Key_Backslash, Qt.Key_CapsLock, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_Semicolon, Qt.Key_Apostrophe, Qt.Key_Return, "L-Shift", Qt.Key_Z, Qt.Key_X, Qt.Key_C, Qt.Key_V, Qt.Key_B, Qt.Key_N, Qt.Key_M, Qt.Key_Comma, Qt.Key_Period, Qt.Key_Slash, "R-Shift", "L-Ctrl", "L-Alt", Qt.Key_Space, "R-Alt", Qt.Key_Menu, "R-Ctrl"]
    
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

    def should_go_next_widget(self,event:QKeyEvent):
        return (
            event.key() == Qt.Key_Left or event.key() == Qt.Key_Right #arrow keys
            ) or (
            event.modifiers() == Qt.ShiftModifier and (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) #shift enter/return
        )

    def update_element(self):
        key_strings = []
        if len(self.unpressed_keys) == 0:
            self.element.text = "Keyboard Passes" 
            return
        for key in self.unpressed_keys:
            if isinstance(key, str):
                key_strings.append(key)
            else:
                key_name = QKeySequence(key).toString().lower()
                key_strings.append(key_name)
        
        s = ",".join(key_strings)
        self.element.text = f"Missing keys: {s}"

    def key_pressed(self, event:QKeyEvent):
        if self.should_go_next_widget(event):
            self.parent.keyPressEvent(event)

        key = self.get_key(event)
        try:
            self.unpressed_keys.remove(key)
        except Exception as e:
            pass
        self.update_element()
        self.view.keyboard.press_key(key)
        