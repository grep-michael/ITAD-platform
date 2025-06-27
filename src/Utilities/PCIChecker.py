from PyQt5.QtWidgets import QMessageBox
import re

class PCIChecker():

    def __init__(self):
        with open("specs/lspci.txt","r") as f:
            self.data = f.read()
    
    def check_problem_devices(self):
        errors = []
        errors += self.check_generic_raid()


        if len(errors)> 0:
            msg = self.format_info_message(errors)
            self.show_info_box(msg)
    
    def format_info_message(self,error_list):
        text = """
- Possible Problem devices found - 
{}
""".format("\n".join(error_list))
        return text

    def show_info_box(self,msg):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Problem Devices detected")
        msgBox.setText(msg)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setStandardButtons(QMessageBox.Ok)
        return msgBox.exec_()

    def check_generic_raid(self):
        def add_error(controller):
            return controller + " -> Raid Controller detected"
        search = re.findall(
            r"RAID bus controller:"
            ,self.data)
        return list(map(add_error,search))
        