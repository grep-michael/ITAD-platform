from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt,QThread
import xml.etree.ElementTree as ET
import os,json,subprocess,time,logging
from datetime import datetime
from Utilities.Utils import CommandExecutor
from Erasure.Services.DriveServices import DriveService
from Erasure.Controllers.DriveModel import DriveModel
from Erasure.Services.ErasureProcesses import *

class WipeConfig:
    WIPE_REAL = False 
    DATE_FORMAT = "%m/%d/%Y"
    TIME_FORMAT = "%H:%M:%S "
    UNMOUNT = "umount {}"
    SMART_COMMAND = "smartctl -ax -j {0}"

class WipeService(QObject):

    update = pyqtSignal(str, str, bool)  # Message, style, Overrride
    exception = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self,drive_model:DriveModel,wipe_method):
        super().__init__()
        self.drive_model = drive_model
        self.wipe_method = wipe_method
        self.drive_service = DriveService(self.drive_model)
        self.drive_service.build_signatures()
        self.py_logger = logging.getLogger("WipeService:{}".format(drive_model.name))

        self.logger_service = WipeLoggerService()

    def start_wipe(self):
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run_method_deterministic)
        self._thread.finished.connect(self.thread_delete)
        self._thread.start()
    
    def emit_update(self,message,style="",override=False):
        self.update.emit(message,style,override)

    def run_method_deterministic(self):
        """
        runs _execute_wipe after determining the proper wipe_method to use
        """
        if self.wipe_method is not None and self.wipe_method is not ErasureProcess:
            self.py_logger.info("running specific method")
            success = self._execute_wipe(self.wipe_method)
        else:
            self.py_logger.info("running method list")
            if Config.DEBUG == "True":
                process_list = [NVMeSecureEraseProcess,ATASecureErasue,PartitionHeaderErasureProcess] #if we're debugging we dont wanna use any long time consuming methods 
            else:
                process_list = [NVMeSecureEraseProcess,ATASecureErasue,RandomOverwriteProcess]


            for command in process_list:
                success = self._execute_wipe(command)
                if success:
                    break

            

        self._clean_up()
        self.logger_service.set_smart_info(self.drive_model.path)
        self.logger_service.add_erasure_fields_to_xml(self.drive_model.xml)
        self.logger_service.end(self.drive_model.name+".json")

    def _execute_wipe(self,wipe_method) -> bool:
        """
        Runs an erasure process
        Returns:
            bool: true if wipe succeeded, false if failed.
        """
        
        wipe_process:ErasureProcess = ErasureProcessFactory.create_method(self.drive_model,wipe_method)
        self.py_logger.info("trying wipe_method:" + wipe_process.DISPLAY_NAME)
        self.logger_service.start(wipe_process)

        try:#ignore missing disks if we're fake wiping
            if not self.drive_service.is_disk_present() and WipeConfig.WIPE_REAL:
                self.drive_service.set_removed()
                self.emit_update("Drive removed","QLabel#status_box { color: red; };")
                self.py_logger.warning("Drive removed")
                time.sleep(5)
                return True

            if self.drive_service.is_cd_drive():
                self.drive_service.set_removed()
                self.emit_update("Drive is CD","QLabel#status_box { color: red; };")
                self.py_logger.warning("Drive is cd")
                time.sleep(5)
                return True
            
            self.emit_update("Wiping disk . . .")

            wipe_process.run()
            while True:
                output:str = wipe_process.readline()
                if output == '' and wipe_process.poll() is not None:
                    break
                if output:
                    self.emit_update(output)
            
            if wipe_process.is_successfull():
                self.emit_update("Command executed Successfully","QLabel#status_box { color: green; } ")
                self.py_logger.info("Command executed Successfully: {}".format(wipe_process.full_output))
                if self.drive_service.check_all_sigs():
                    self.emit_update("Signature check passed","QLabel#status_box { color: green; } ")
                    self.py_logger.info("Signature check passed")
                    self.logger_service.set_success()
                    return True

                else:
                    self.emit_update("Signature check Failed","QLabel#status_box { color: red; } ")
                    self.py_logger.error("Signature check Failed")
                    return False
            else:
                self.emit_update("Command executed Unsuccessfully","QLabel#status_box { color: red; } ")
                self.py_logger.warning("Command executed Unsuccessfully: {}".format(wipe_process.full_output))
                time.sleep(5)
                return False

        except Exception as e:
            print(e)
            self.exception.emit(str(e))
            self.py_logger.error(e)
            
    
    def _clean_up(self):
        print(self.drive_model.name,":","thread finished: {}".format(self.drive_model.name))
        self._thread.quit()

    def thread_delete(self):
        self._thread.deleteLater()
        

class WipeLoggerService:
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
        self.log["End_Date"] = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        self.log["End_Time"] = datetime.now().strftime(WipeConfig.TIME_FORMAT)
        self.log["Erasure_Time"] = str(self.log["End_Time_Raw"]-self.log["Start_Time_Raw"])
        self.clean_log_for_json()
        del self.log["Smart_Info"]
        if not os.path.exists("specs/erasures"):
            os.makedirs("specs/erasures")

        with open("specs/erasures/{}".format(logname),'w') as f:
            json.dump(self.log,f,indent=4)
            
    def clean_log_for_json(self):
        clean_log = {}
        for key,value in self.log.items():
            try:
                #if the value isnt json serializable we just skip it
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
        ed.text = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        xml.append(ec)
        xml.append(em)
        xml.append(er)
        xml.append(ed)
        self.log["Model"] = xml.find(".//Model").text
        self.log["Serial_Number"] = xml.find(".//Serial_Number").text

    def start(self,wipe_process:ErasureProcess):
        #print("wipe logger started")
        self.method = wipe_process
        self.log["Result"] = "Failed" #we assume a failed erasure, we call set_success later if the wipe succeeds
        self.log["Start_Time_Raw"] = datetime.now()
        self.log["Start_Date"] = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        self.log["Start_Time"] = datetime.now().strftime(WipeConfig.TIME_FORMAT)
        self.log["Method"] = wipe_process.method_name
        self.log["Compliance"] = wipe_process.compliance
    
    def set_smart_info(self,path):
        
        smart_info = CommandExecutor.run([WipeConfig.SMART_COMMAND.format(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).stdout.decode('utf-8')
        try:
            smart_info = json.loads(smart_info)
            del smart_info["json_format_version"]
            del smart_info["smartctl"] 
            self.log["Smart_Info"] = smart_info
        except json.decoder.JSONDecodeError:
            self.log["Smart_Info"] = "Failed to decode smart info: {}".format(smart_info)
    
  