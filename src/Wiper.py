from time import sleep
from datetime import datetime
from abc import ABC, abstractmethod
from subprocess import CompletedProcess
from Utils import CommandExecutor
import xml.etree.ElementTree as ET
import subprocess,json,logging
from PyQt5.QtCore import QObject,pyqtSignal


WIPE_REAL = True

UNMOUNT = "umount {}"
SIGNATURES_COMMAND = "wipefs --no-act -J -O UUID,LABEL,LENGTH,TYPE,OFFSET,USAGE,DEVICE {0}"
SMART_COMMAND = "smartctl -ax -j {0}"


class Drive(QObject):

    update = pyqtSignal(str,str,int)
    exception = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self,xml:ET):
        super().__init__()
        name = xml.find(".//Name").text
        self.logger = logging.getLogger("Drive_{}".format(name))
        self.name = name
        self.xml = xml
        self.path = "/dev/"+name
        self.logger.info("created drive".format(self.path))
        self.build_signatures()
    
    def set_wipe_method(self,method:'WipeMethod'):
        self.wipe_method = method

    def emit_update(self,msg,style="",override=0):
        self.update.emit(msg,style,override)

    def start_wipe_log(self) -> dict:
        date_format = "%H:%M:%S %d-%m-%Y"
        erasure_log = {}
        if self.wipe_method.method_name is not None:
            erasure_log["Erasure_Method"] = self.wipe_method.method_name
        else:
            erasure_log["Erasure_Method"] = "start_wipe_log called before set_wipe_method"
        erasure_log["Start_Time"] = datetime.now().strftime(date_format)
        self.erasure_log = erasure_log
    
    def finish_wipe_log(self,wipe_result:'WipeResult'):
        end = datetime.now()
        self.set_wipe_log_field("End_Time",end.strftime("%H:%M:%S %d-%m-%Y"))
        self.set_wipe_log_field("Time_Difference",str(end-wipe_result.start_time))
        smart_info = CommandExecutor.run([SMART_COMMAND.format(self.path)],stdout=-1,stderr=-1,shell=True).stdout.decode('utf-8')
        smart_info = json.loads(smart_info)
        self.set_wipe_log_field("Model",smart_info["model_name"])
        self.set_wipe_log_field("Serial_Number",smart_info["serial_number"])
        del smart_info["json_format_version"]
        del smart_info["smartctl"]
        self.set_wipe_log_field("Smart_Info",smart_info)

        self.add_erasure_fields_to_xml()

        with open("specs/erasure.json",'w') as f:
            f.write(json.dumps(self.erasure_log))

    def add_erasure_fields_to_xml(self):
        em = ET.Element("Erasure_Method")
        em.text = self.wipe_method.method_name
        er = ET.Element("Erasure_Results")
        er.text = self.erasure_log["Result"]
        ed = ET.Element("Erasure_Date")
        ed.text = datetime.now().strftime("%d-%m-%Y")
        self.xml.append(em)
        self.xml.append(er)
        self.xml.append(ed)

    def set_wipe_log_field(self,field:str,value):
        self.erasure_log[field] = value

    def wipe(self):
        self.emit_update("Wiping Disk")
        self.logger.info("Disk Wipe Command")
        self.start_wipe_log()
        result = self.wipe_method.wipe(self.path)
        while True:
            output = result.process.stdout.readline()
            if output == '' and result.process.poll() is not None:
                break
            if output:
                self.emit_update(output)

        
        sig_check = self.check_all_sigs()
        self.set_wipe_log_field("signature_check",sig_check)

        if result.is_std_err():
            error = "Disk Wipe Failed: {}".format(result.get_std_err())
            self.logger.error(error)
            self.set_wipe_log_field("cmd_stderr",error)
            self.emit_update(error,"DriveWidget { border: 2px solid red; }; QLabel#Status_box { color: red; };",True)    
            sleep(4)

        if sig_check is False:
            self.emit_update("Disk wipe failed signature check","DriveWidget { border: 2px solid red; } QLabel#Status_box { color: red; };",True)
            self.logger.error("disk failed signature check: {}".format(result.get_std_out()))
            self.set_wipe_log_field("Result","Failed")
        else:
            self.emit_update("Disk Wiped"," QLabel#Status_box { color: green; } ")
            self.set_wipe_log_field("Result",'Passed')
        
        self.finish_wipe_log(result)
        self.finished.emit()

    def check_all_sigs(self):
        """
        All signatures should be the same, theyve either been wiped or havnt
        """
        failed = all(self.check_signature_zero(sig) for sig in self.signatures)
        #print(self.name,failed)
        return failed

    def check_signature_zero(self,signature) -> bool:
        """
        True of sig is different than its original value, false if its not
        """
        self.logger.info("checking Signature:{}".format(signature))

        current_bytes = self.read_sig(signature)
        if current_bytes != signature["original_bytes"]:
            return True
        return False

    def build_signatures(self):
        print("Getting Signatures for drive: {}".format(self.path))
        ret = CommandExecutor.run([SIGNATURES_COMMAND.format(self.path)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.signatures = []
        if ret.returncode == 0:
            drive_signatures = json.loads(ret.stdout.decode("utf-8"))
            self.signatures = drive_signatures["signatures"]
        
        for sig in self.signatures:
            _bytes = self.read_sig(sig)
            sig["original_bytes"] = _bytes

        self.logger.info("Drive {0} has signatures: {1}".format(self.path,self.signatures))

    def read_sig(self,signature:dict) -> bytes:
        path = "/dev/"+signature["device"]
        offset = int(signature["offset"],16)
        length = signature["length"]
        with open(path,"rb") as f:
            f.seek(offset)
            sig_bytes = f.read(length)
        return sig_bytes 



class WipeMethod(ABC):

    def __init__(self):
        self.method_name = "Generic Wipe"

    @abstractmethod
    def wipe(self,drive:str) -> 'WipeResult':
        """
        Args:
            drive (str) - drive path to be wiped, in format /dev/sdx*
        return:
            WipeResult -> true if command success false if failed
        """
        raise NotImplementedError()

class WipeResult():

    return_code_dict = {
        0:"General Success",
        1:"Genral error",
        2:"Misuse of shell builtins",
        128:"Command invoked cannot execute",
        127:"Command not found",
        128:"Invaild argument to exit",
        255:"exit status out of range"
    }

    def __init__(self,process:CompletedProcess=None,start_time:datetime=datetime.now()):
        self.start_time = start_time
        self.process = process

    def is_std_err(self)->bool:
        """
        return:
            bool -> true if theres stderr output
        """
        if self.process is None or self.process.stderr is None:
            return False
        
        return len(self.process.stderr.read().strip())>0
    def get_std_out(self):
        if self.process is None:
            return "Process is None"
        return self.process.stdout.read()
    def get_std_err(self):
        if self.process is None:
            return "Process is None"
        return self.process.stderr.read()

class PartitionHeaderErasure(WipeMethod):

    def __init__(self):
        super().__init__()
        self.method_name = "PartitionHeaderErasure"

    def wipe(self,drive):

        if WIPE_REAL:
            WIPE_COMMAND = "wipefs -af {0}*"
        else:
            WIPE_COMMAND = "wipefs --all --force --no-act {0}*"

        if "/dev/" not in drive:
            raise Exception("wipe method recived unexpected input: {}\nExpected input format: /dev/sdx".format(drive))
        drive = drive + "*"
        command = WIPE_COMMAND.format(drive)
        #CommandExecutor.run([UNMOUNT.format(drive)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)


        result = WipeResult(process=process)
        #result.build_wipe_log(self.method_name)
        return result

class FakeWipe(WipeMethod):
    def __init__(self):
        self.method_name = "Fake Wipe"
    
    def wipe(self,drive):
        funny_command = "echo 1;sleep 1;echo 2;sleep 1;echo 3;sleep 1;echo 4;sleep 1;echo 5;sleep 1;echo 6;sleep 1;echo 7;sleep 1;echo 8;sleep 1;echo 9;sleep 1;echo 10"
        #funny_command = "shred -f -n 1 -s 1G -v {}".format(drive)
        ret = subprocess.Popen([funny_command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)

        return WipeResult(process=ret)

class NISTErasure(WipeMethod):
    def __init__(self):
        super().__init__()
        self.method_name = "NIST 800-88"
    
    def wipe(self,drive):

        if WIPE_REAL:
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

        return WipeResult(process=ret)