from datetime import datetime

class Message():
    pass

STATUS_LABEL = "QLabel#status_box"
DRIVE_ITEM_FRAME = "QFrame#drive_item_view"

STYLES = {
    "Error":"{} {{ border: 5px solid red; }} QLabel#status_box {{ color: red; }}",
    "Success":"{} {{ border: 5px solid green; }} QLabel#status_box {{ color: green; }}",
    "Standard":"{} {{ border: 5px solid black; }} QLabel#status_box {{ color: black; }};"
}


class ErasureTimeUpdateMessage(Message):
    def __init__(self):
        self.time_now_raw = datetime.now()
        self.time_now_str = self.time_now_raw.strftime("%H:%M:%S")

class ErasureStatusUpdateMessage(Message):
    def __init__(self,message:str,stylesheet:str=STYLES["Standard"].format(DRIVE_ITEM_FRAME),override:bool=True):
        self.message = message
        self.stylesheet = stylesheet
        self.override = override

class StartErasureMessage(ErasureStatusUpdateMessage):
    def __init__(self):
        self.time_now_raw = datetime.now()
        self.time_now_str = self.time_now_raw.strftime("%H:%M:%S")
        super().__init__("Erasure Started", STYLES["Standard"].format(DRIVE_ITEM_FRAME))

class ErasureErrorMessage(ErasureStatusUpdateMessage):
    def __init__(self, message:str):
        super().__init__(message, STYLES["Error"].format(DRIVE_ITEM_FRAME))

class ErasureSuccessMessage(ErasureStatusUpdateMessage):
    def __init__(self, message:str):
        super().__init__(message, STYLES["Success"].format(DRIVE_ITEM_FRAME))
        
    