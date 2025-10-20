from Generics import ITADView
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence




class KeyboardTestView(ITADView):

    

    def __init__(self):
        super().__init__()
        self.keyboard:Keyboard
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.header = QLabel("Keyboard test")
        self.header.setAlignment(Qt.AlignCenter)

        self.keyboard = Keyboard()

        self.vbox.addWidget(self.header)
        self.vbox.addWidget(self.keyboard)
        self.vbox.addWidget(QLabel())

        self.setLayout(self.vbox)


class KeyboardButton(QPushButton):
    def __init__(self,text):
        super().__init__(text)
        self.has_been_pressed:bool = False

class Keyboard(QWidget):
    
    keyboard_layout = [
    # Row 0: Escape, Function keys, and Print keys
    # The Function keys do not work on parted magic which is where we are running this script, so for now they are disabled
    #[Qt.Key_Escape, Qt.Key_F1, Qt.Key_F2, Qt.Key_F3, Qt.Key_F4, Qt.Key_F5,
    # Qt.Key_F6, Qt.Key_F7, Qt.Key_F8, Qt.Key_F9, Qt.Key_F10, Qt.Key_F11, Qt.Key_F12, Qt.Key_Print],
    [Qt.Key_Escape, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, Qt.Key_Print],

    # Row 1: `123... Backspace
    [Qt.Key_QuoteLeft, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5,
     Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_0, Qt.Key_Minus, Qt.Key_Equal, Qt.Key_Backspace],
    
    # Row 2: Tab and QWERTY
    [Qt.Key_Tab, Qt.Key_Q, Qt.Key_W, Qt.Key_E, Qt.Key_R, Qt.Key_T,
     Qt.Key_Y, Qt.Key_U, Qt.Key_I, Qt.Key_O, Qt.Key_P, Qt.Key_BracketLeft,
     Qt.Key_BracketRight, Qt.Key_Backslash],
    
    # Row 3: Caps Lock and ASDF...
    [Qt.Key_CapsLock, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_F, Qt.Key_G,
     Qt.Key_H, Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_Semicolon, Qt.Key_Apostrophe, Qt.Key_Return],
    
    # Row 4: Shift and ZXCV...
    ["L-Shift", Qt.Key_Z, Qt.Key_X, Qt.Key_C, Qt.Key_V, Qt.Key_B,
     Qt.Key_N, Qt.Key_M, Qt.Key_Comma, Qt.Key_Period, Qt.Key_Slash, "R-Shift"],
    
    # Row 5: Ctrl, Win, Alt, Space, AltGr, Menu, Ctrl
    [0,0,"L-Ctrl", "Win", "L-Alt", Qt.Key_Space, "R-Alt", Qt.Key_Menu, "R-Ctrl",0,0]
]   #Qt.Key_Meta <- windows key

    wide_keys = {
        Qt.Key_Shift: 2,
        Qt.Key_Return: 2,
        Qt.Key_Space: 4,
        "R-Shift" : 2,
        "L-Shift" : 2,
    }

    def __init__(self):
        super().__init__()
        self.key_buttons:dict[KeyboardButton] = {}

        self.initUI()

    def release_key(self,key_code):
        if key_code in self.key_buttons:
            btn:KeyboardButton = self.key_buttons[key_code]
            btn.setStyleSheet("background-color: #90EE90 ;")
    
    def press_key(self,key_code):
        if key_code in self.key_buttons:
            btn:KeyboardButton = self.key_buttons[key_code]
            #if not btn.has_been_pressed:
            btn.setStyleSheet("background-color: #C6F6C6;")
            return True
        return False
    
    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignCenter)

         # Create buttons and add them to the layout
        for row_idx, row in enumerate(self.keyboard_layout):
            col_idx = 0
            for key in row:
                label = self.get_key_label(key)
                button = KeyboardButton(label)
                button.setFocusPolicy(Qt.NoFocus)
                if label == "":
                    button.hide()
                col_span = self.wide_keys.get(key, 1)
                self.grid.addWidget(button, row_idx, col_idx,1,col_span)
                self.key_buttons[key] = button
                col_idx+=col_span
        self.setLayout(self.grid)
        self.setFocusPolicy(Qt.StrongFocus)

    def get_key_label(self,key):
        if isinstance(key, str):
            return key.replace("L-", "").replace("R-", "")
        
        return QKeySequence(key).toString()
    