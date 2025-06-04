from datetime import datetime

class Message():
    pass

STATUS_BOX_IDENTIFIER = "QLabel#status_box"

STYLES = {
    "Error":"{} {{ color: red; }};",
    "Success":"{} {{ color: green; }};",
    "Standard":"{} {{ color: black; }};"
}


class ErasureTimeUpdateMessage(Message):
    def __init__(self):
        self.time_now_raw = datetime.now()
        self.time_now_str = self.time_now_raw.strftime("%H:%M:%S")

class ErasureStatusUpdateMessage(Message):
    def __init__(self,message:str,stylesheet:str=STYLES["Standard"].format(STATUS_BOX_IDENTIFIER),override:bool=True):
        self.message = message
        self.stylesheet = stylesheet
        self.override = override

class StartErasureMessage(ErasureStatusUpdateMessage):
    def __init__(self):
        self.time_now_raw = datetime.now()
        self.time_now_str = self.time_now_raw.strftime("%H:%M:%S")
        super().__init__(self.time_now_str, STYLES["Standard"].format(STATUS_BOX_IDENTIFIER), True)

class ErasureErrorMessage(ErasureStatusUpdateMessage):
    def __init__(self, message:str):
        super().__init__(message, STYLES["Error"].format(STATUS_BOX_IDENTIFIER), True)

class ErasureSuccessMessage(ErasureStatusUpdateMessage):
    def __init__(self, message:str):
        super().__init__(message, STYLES["Success"].format(STATUS_BOX_IDENTIFIER), True)
        
    