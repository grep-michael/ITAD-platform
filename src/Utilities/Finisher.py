from Services.DataRefiner import *
from PyQt5.QtWidgets import QMessageBox
import re

class Finisher():
    
    def finialize_process(root):
        LogRefiner.Refine_data()
        XMLTreeRefiner.Refine_tree(root)

        pci = PCIChecker()
        pci.check_problem_devices()

        


class PCIChecker():

    def __init__(self):
        with open("specs/lspci.txt","r") as f:
            self.data = f.read()
    
    def check_problem_devices(self):
        comet_lake_raid = self.check_comet_lake_controller()

        msg = self.format_info_message(comet_lake_raid)
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
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        return msgBox.exec_()

    def check_comet_lake_controller(self):
        def add_error(controller):
            return controller + " -> Invaild raid controller found disbale in bios and run script again"
        search = re.findall(
            r"RAID bus controller:.*Comet Lake"
            ,self.data)
        return map(add_error,search)
        