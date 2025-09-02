from Utilities.Utils import CommandExecutor
import xml.etree.ElementTree as ET
import subprocess,json,logging,os
from Erasure.Controllers.DriveModel import DriveModel

class PhysicalDriveConfig:
    SIGNATURES_COMMAND = "wipefs --no-act -J -O UUID,LABEL,LENGTH,TYPE,OFFSET,USAGE,DEVICE {0}"


class DriveService:

    def __init__(self,drive_model:DriveModel):
        self.model = drive_model
        self.path = drive_model.path
        self.logger = logging.getLogger("")
        self.build_signatures()

    def check_all_sigs(self):
        """
        return true if all signatures are changed from their original state
        """
        failed = all(self.compare_sig_bytes(sig) for sig in self.signatures)
        #print(self.name,failed)
        return failed

    def build_signatures(self):
        ret = CommandExecutor.run([PhysicalDriveConfig.SIGNATURES_COMMAND.format(self.path)],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.signatures = []
        if ret.returncode == 0:
            drive_signatures = json.loads(ret.stdout.decode("utf-8"))
            self.signatures = drive_signatures["signatures"]
        if len(drive_signatures) <=0 :
            self.logger.info("No partition signatures detected, drive is already erased")
            
        for sig in self.signatures:
            _bytes = self._read_sig(sig)
            sig["original_bytes"] = _bytes

    def compare_sig_bytes(self,signature):
        """
        get current bytes of a signature and compare them to the the original bytes recored when build_signatures was called
        """
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
        """
        returns true if disk shows up using `ls`
        """
        ret = subprocess.run(["ls {}".format(self.path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).returncode
        if ret == 0:
            return True
        return False
    
    def is_cd_drive(self):
        return "cdrom" in self.path or "/dev/sr" in self.path

    def set_removed(self,removed=True):
        """
        Set the associated drive_model Removed tag
        """
        self.model.set_removed(removed)