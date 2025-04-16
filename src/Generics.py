from PyQt5.QtWidgets import QWidget,QFrame

class ITADWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.has_been_viewed = False
        
    def verify(self):
        """
        Called in the main window when the program tries to move to the next widget 
        """
        raise NotImplementedError()

    def pre_display_update(self,parent):
        """
        Called before the widget is set as the current widget in the main window
        """
        return
