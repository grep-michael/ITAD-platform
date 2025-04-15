from PyQt5.QtWidgets import QWidget,QFrame

class ITADWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.has_been_viewed = False
        
    def verify(self):
        raise NotImplementedError()
