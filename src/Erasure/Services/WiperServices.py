from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt,QThread
import xml.etree.ElementTree as ET
import os,json,subprocess,time,logging
from Utilities.Utils import CommandExecutor
from Erasure.Services.DriveServices import DriveService
from Erasure.Controllers.DriveModel import DriveModel
from Erasure.Services.ErasureProcesses import *
from datetime import datetime
from io import TextIOWrapper
from Erasure.Messages import *
import threading

class WipeConfig:
    DATE_FORMAT = "%m/%d/%Y"
    TIME_FORMAT = "%H:%M:%S "
    UNMOUNT = "umount {}"
    SMART_COMMAND = "smartctl -ax -j {0}"

class WipeService(QObject):

    update = pyqtSignal(Message)  # Message, style, Overrride
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
    
    def emit_update(self,message:Message):
        self.update.emit(message)

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
        self.logger_service.end()

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
            if not self.drive_service.is_disk_present() and Config.DEBUG =="False":
                self.drive_service.set_removed()
                self.emit_update(ErasureErrorMessage("Drive removed"))
                self.py_logger.warning("Drive removed")
                time.sleep(5)
                return True

            if self.drive_service.is_cd_drive():
                self.drive_service.set_removed()
                self.emit_update("Drive is CD","QLabel#status_box { color: red; };")
                self.py_logger.warning("Drive is cd")
                time.sleep(5)
                return True
            
            self.emit_update(StartErasureMessage())

            wipe_process.run()
            self.start_timer_thread()
            self.py_logger.info("timer thread started")
            while True:
                output:str = wipe_process.readline()
                if output == '' and wipe_process.poll() is not None:
                    break
                if output:
                    self.emit_update(ErasureStatusUpdateMessage(output))

            self.end_timer_thread()
            self.py_logger.info("timer thread stopped")

            if wipe_process.is_successfull():
                
                self.emit_update(ErasureSuccessMessage("Command executed Successfully"))
                
                self.py_logger.info("Command executed Successfully: {}".format(wipe_process.full_output))
                if self.drive_service.check_all_sigs():
                    
                    self.emit_update(ErasureSuccessMessage("Signature check passed"))
                    #self.emit_update("Signature check passed","QLabel#status_box { color: green; } ")
                    self.py_logger.info("Signature check passed")
                    
                    self.logger_service.set_success()
                    return True

                else:
                    self.emit_update(ErasureErrorMessage("{}\nSignature check Failed".format(wipe_method.DISPLAY_NAME)))
                    self.py_logger.error("Signature check Failed")
                    return False
            else:
                self.emit_update(ErasureErrorMessage("{}\nSignature check Failed".format(wipe_method.DISPLAY_NAME)))
                self.py_logger.warning("Command executed Unsuccessfully: {}".format(wipe_process.full_output))
                time.sleep(5)
                return False

        except Exception as e:
            print(e)
            self.exception.emit(str(e))
            self.py_logger.error(e)
    
    def timer_loop(self,event:threading.Event):
        while not event.is_set():
            self.emit_update(ErasureTimeUpdateMessage())
            time.sleep(1)

    def end_timer_thread(self):
        self.timer_thread_event.set()
        self.timer_thread.join()


    def start_timer_thread(self):
        self.timer_thread_event = threading.Event()
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True,args=(self.timer_thread_event,),name="TimerLoop")
        self.timer_thread.start()


    def _clean_up(self):
        print(self.drive_model.name,":","thread finished: {}".format(self.drive_model.name))
        self._thread.quit()

    def thread_delete(self):
        self._thread.deleteLater()

class LogDictionary(dict):

    def __init__(self):
        self.json = {}
        self.json_file:TextIOWrapper

    def make_log_file(self,filename):
        self.json_file = open(filename,'w')

    def __setitem__(self, key, value):
        # Custom logic before setting the value
        super().__setitem__(key,value)
        #self[key] = value
        
        try:
            #if the value isnt json serializable we just skip it
            json.dumps(value)
            self.json[key] = value

            self.json_file.flush()
            json.dump(self.json,self.json_file,indent=4)
            self.json_file.seek(0)
            
        except (TypeError, OverflowError):
            pass
    def save_and_close_log(self):
        self.json_file.close()
        with open(self.json_file.name,"w") as f:
            json.dump(self.json,f,indent=4)
        
class WipeLoggerService:
    def __init__(self):
        self.log = LogDictionary()
        

    def set_success(self):
        self.log["Result"] = "Passed"

    def end(self):

        self.log["End_Time_Raw"] = datetime.now()
        self.log["End_Date"] = datetime.now().strftime(WipeConfig.DATE_FORMAT)
        self.log["End_Time"] = datetime.now().strftime(WipeConfig.TIME_FORMAT)
        self.log["Erasure_Time"] = str(self.log["End_Time_Raw"]-self.log["Start_Time_Raw"])

        self.log.save_and_close_log()
        
            
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
        
        self.method = wipe_process
        if not os.path.exists("specs/erasures"):
            os.makedirs("specs/erasures")
        
        self.log.make_log_file("specs/erasures/{}.json".format(wipe_process.drive_model.name))
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
    
  