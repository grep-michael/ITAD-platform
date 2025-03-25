from time import sleep
from pprint import pprint
from datetime import datetime
from abc import ABC, abstractmethod
from subprocess import CompletedProcess
from Utils import CommandExecutor
import xml.etree.ElementTree as ET
import subprocess,json,logging,os
from PyQt5.QtCore import QObject,pyqtSignal

class WipeConfig():
    WIPE_REAL = True
    DATE_FORMAT = "%H:%M:%S %d-%m-%Y"
    UNMOUNT = "umount {}"
    SIGNATURES_COMMAND = "wipefs --no-act -J -O UUID,LABEL,LENGTH,TYPE,OFFSET,USAGE,DEVICE {0}"
    SMART_COMMAND = "smartctl -ax -j {0}"

class PhysicalDrive():
    def __init__(self,drive_path:str):
        self.path = drive_path
        self.build_signatures()

    def check_all_sigs(self):
        """
        All signatures should be the same, theyve either been wiped or havnt
        """
        failed = all(self.compare_sig_bytes(sig) for sig in self.signatures)
        #print(self.name,failed)
        return failed

    def build_signatures(self):
        ret = CommandExecutor.run([WipeConfig.SIGNATURES_COMMAND.format(self.path)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.signatures = []
        if ret.returncode == 0:
            drive_signatures = json.loads(ret.stdout.decode("utf-8"))
            self.signatures = drive_signatures["signatures"]
        
        for sig in self.signatures:
            _bytes = self._read_sig(sig)
            sig["original_bytes"] = _bytes

    def compare_sig_bytes(self,signature):
        current_bytes = self._read_sig(signature)
        if current_bytes != signature["original_bytes"]:
            return True
        return False    

    def _read_sig(self,signature:dict) -> bytes:
        path = "/dev/"+signature["device"]
        offset = int(signature["offset"],16)
        length = signature["length"]
        with open(path,"rb") as f:
            f.seek(offset)
            sig_bytes = f.read(length)
        return sig_bytes 

    def is_disk_present(self):
        ret = subprocess.run(["ls {}".format(self.path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).returncode
        if ret == 0:
            return True
        return False

class WipeObserver(QObject):
    
    update = pyqtSignal(str,str,int)
    exception = pyqtSignal(str)
    finished = pyqtSignal()

    def emit_update(self,msg,style="",override=0):
        self.update.emit(msg,style,override)

    def finish_wipe(self):
        self.wipe_logger.set_smart_info(self.drive_path)
        self.wipe_logger.add_erasure_fields_to_xml(self.drive_xml)
        self.wipe_logger.end(self.name+".json")
        self.finished.emit()

    def __init__(self,drive_info:ET):
        super().__init__()
        self.name = drive_info.find(".//Name").text
        self.drive_xml = drive_info
        self.py_pogger = logging.getLogger("Drive_{}".format(self.name))
        self.wipe_logger = WipeLogger()
        self.drive_path = "/dev/" + self.name
        self.physical_drive = PhysicalDrive(self.drive_path)

    def set_method(self,m):
        self._set_method = m

    def run_method_deterministic(self):
        method = self._set_method
        if method != WipeMethod:
            self._run_method_on_drive(method)
        else:        
            appropriate_methods = [NVMeSecureErase,PartitionHeaderErasure]
            for method in appropriate_methods:
                sucess = self._run_method_on_drive(method)
                if sucess:
                    break
                self.emit_update("Method {} failed, trying next".format(method),"QLabel#Status_box { color: red; };")
                sleep(5)

        self.finish_wipe()
            
    def _run_method_on_drive(self,method:'WipeMethod')-> bool:
        """
        returns true if method successfully erased the drive 
        """
        method = method()
        self.wipe_logger.start(method)

        if not self.physical_drive.is_disk_present():
            self.drive_xml.append(ET.Element("Removed"))
            self.emit_update("Drive removed","QLabel#Status_box { color: red; };")
            return True
        self.emit_update("Wiping Disk")
        self.py_pogger.info("wiping disk with: {}".format(method.method_name))
        
        method.erase_with_callback(self.drive_path,self.emit_update)
        print(method.process)
        if not method.is_successfull():
            self.emit_update("{}.is_successfull returned false".format(method.method_name),"QLabel#Status_box { color: red; };")
            self.py_pogger.warning("{}.is_successfull returned false".format(method.method_name))
            return False

        sig_check = self.physical_drive.check_all_sigs()
        if sig_check:
            self.emit_update("Disk Wiped","DriveWidget { border: 2px solid green; } QLabel#Status_box { color: green; } ",True)
            self.py_pogger.info("Disk Wipe successfull")
            self.wipe_logger.set_success()
            return True
        
        self.emit_update("Disk wipe failed signature check","DriveWidget { border: 2px solid red; } QLabel#Status_box { color: red; };",True)
        self.py_pogger.error("Signature check failed")
        return False
            
class WipeLogger():
    def __init__(self):
        self.log = {}

    def set_success(self):
        self.log["Result"] = "Passed"

    def end(self,logname="erasure.json"):
        """
        call start before this
        Args:
            logname (str) -> name for log, input expect to end with .json, e.g /logname.json
        """
        self.log["End_Time_Raw"] = datetime.now()
        self.log["End_Time"] = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        self.log["Erasure_Time"] = str(self.log["End_Time_Raw"]-self.log["Start_Time_Raw"])
        self.clean_log_for_json()

        if not os.path.exists("specs/erasures"):
            os.makedirs("specs/erasures")

        with open("specs/erasures/{}".format(logname),'w') as f:
            json.dumps(self.log,f,indent=4)
            
    def clean_log_for_json(self):
        clean_log = {}
        for key,value in self.log.items():
            try:
                json.dumps(value)
                clean_log[key] = value
            except (TypeError, OverflowError):
                pass
        #move smart info to the end
        smart_info = clean_log.pop("Smart_Info")
        clean_log["Smart_Info"] = smart_info
        self.log = clean_log

    def add_erasure_fields_to_xml(self,xml):
        ec = ET.Element("Erasure_Compliance")
        ec.text = self.method.compliance
        em = ET.Element("Erasure_Method")
        em.text = self.log["Method"]
        er = ET.Element("Erasure_Results")
        er.text = self.log["Result"]
        ed = ET.Element("Erasure_Date")
        ed.text = datetime.now().strftime("%d-%m-%Y")
        xml.append(ec)
        xml.append(em)
        xml.append(er)
        xml.append(ed)

    def start(self,method:'WipeMethod'):
        self.method = method
        self.log["Result"] = "Failed" #we assume a failed erasure, we call set_success later if the wipe succeeds
        self.log["Start_Time_Raw"] = datetime.now()
        self.log["Start_Time"] = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        self.log.update(method.build_erasure_info())
    
    def set_smart_info(self,path):
        smart_info = CommandExecutor.run([WipeConfig.SMART_COMMAND.format(path)],stdout=-1,stderr=-1,shell=True).stdout.decode('utf-8')
        smart_info = json.loads(smart_info)
        if smart_info["smartctl"]["exit_status"] == 0:
            self.log["Model"] = smart_info["model_name"]
            self.log["Serial_Number"] = smart_info["serial_number"]
        del smart_info["json_format_version"]
        del smart_info["smartctl"] 
        self.log["Smart_Info"] = smart_info
        
class WipeMethod():

    def __init__(self):
        self.method_name = "None"
        self.compliance = "None"

    @abstractmethod
    def wipe(self,drive:str) -> 'subprocess.Popen':
        """
        Args:
            drive (str) - drive path to be wiped, in format /dev/sdx*
        return:
            subprocess.Popen -> Popen for the specific erasure command
        """
        raise NotImplementedError()
    
    def erase_with_callback(self,drive:str,update_callback:callable):
        """
        will call wipe and put output to update_callback function
        """
        process = self.wipe(drive)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                update_callback(output)
        self.process = process

    def is_successfull(self):
        retcode = self.process.returncode
        return retcode == 0

    def build_erasure_info(self) -> dict:
        info = {}
        info["Method"] = self.method_name
        info["Compliance"] = self.compliance
        return info

class PartitionHeaderErasure(WipeMethod):

    def __init__(self):
        super().__init__()
        self.method_name = "Partition_Header_Erasure"\

    def wipe(self,drive):

        if WipeConfig.WIPE_REAL:
            WIPE_COMMAND = "wipefs -af {0}*"
        else:
            WIPE_COMMAND = "wipefs --all --force --no-act {0}*"

        if "/dev/" not in drive:
            raise Exception("wipe method recived unexpected input: {}\nExpected input format: /dev/sdx".format(drive))
        command = WIPE_COMMAND.format(drive)
        #CommandExecutor.run([UNMOUNT.format(drive)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        #result.build_wipe_log(self.method_name)
        return process

class FakeWipe(WipeMethod):
    def __init__(self):
        super().__init__()
        self.method_name = "Fake Wipe"
    
    def wipe(self,drive):
        funny_command = "echo 1;sleep 1;echo 2;sleep 1;echo 3;sleep 1;echo 4;sleep 1;echo 5;sleep 1;echo 6;sleep 1;echo 7;sleep 1;echo 8;sleep 1;echo 9;sleep 1;echo 10"
        #funny_command = "shred -f -n 1 -s 1G -v {}".format(drive)
        ret = subprocess.Popen([funny_command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)

        return ret

class RandomOverwrite(WipeMethod):
    def __init__(self):
        super().__init__()
        self.method_name = "Random_Overwrite"
        self.compliance = "NIST 800-88 Revision 1"
    
    def wipe(self,drive):

        if WipeConfig.WIPE_REAL:
            WIPE_COMMAND = "shred -f -n 1 -v {0}"
        else:
            WIPE_COMMAND = """echo {0};sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...585MiB/5.0GiB 11%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...1.2GiB/5.0GiB 24%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...1.8GiB/5.0GiB 36%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...2.4GiB/5.0GiB 49%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...3.1GiB/5.0GiB 63%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...3.8GiB/5.0GiB 76%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...4.4GiB/5.0GiB 89%\";sleep 1;
echo \"shred: /dev/sda: pass 1/1 (random)...5.0GiB/5.0GiB 100%\";sleep 1;
"""


        ret = subprocess.Popen([WIPE_COMMAND.format(drive)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)

        return ret

class NVMeSecureErase(WipeMethod):
    def __init__(self):
        super().__init__()
        self.method_name = "NVMeSecureErasure"
        self.compliance = "NIST 800-88 Revision 1"
    
    def wipe(self,drive:str):
        if WipeConfig.WIPE_REAL:
            WIPE_COMMAND = "nvme format --force {}"
        else:
            WIPE_COMMAND = "echo fake nvme wipe {}"
        ret = subprocess.Popen([WIPE_COMMAND.format(drive)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)

        return ret
        
