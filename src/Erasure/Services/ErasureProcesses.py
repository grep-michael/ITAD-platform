from Erasure.Controllers.DriveModel import DriveModel
import subprocess

class ErasureProcessFactory:
    WIPE_REAL = True
    def create_method(drive_model:DriveModel,method:'ErasureProcess'):
        if method is None:
            return PartitionHeaderErasureProcess(drive_model)
        return method(drive_model)

class ErasureProcess(subprocess.Popen):
    DISPLAY_NAME = "Default"

    def __init__(self,drive_model:DriveModel):
        self.method_name = "Default"
        self.compliance = "None"
        self.drive_model = drive_model
        self.path = drive_model.path
        self.WIPE_COMMAND = "echo \"fake wipe {}\""
        self.args = {
                "shell":True,
                "stdout":subprocess.PIPE,
                "stderr":subprocess.STDOUT,
                "text":True,
                }
        
    def run(self):
        """
        This function inializes the super class causing the command to be run,
        also meaning that Popen values like .returncode cant be used before we call this function
        """
        super().__init__(
            [self.WIPE_COMMAND.format(self.path)],
            **self.args
        )

    def is_successfull(self):
        retcode = self.returncode
        return retcode == 0
    
class PartitionHeaderErasureProcess(ErasureProcess):

    DISPLAY_NAME = "Partition Header Erasure"

    def __init__(self,drive_model:DriveModel):
        super().__init__(drive_model)
        self.method_name = "Partition Header Erasure"

        
        if ErasureProcessFactory.WIPE_REAL:
            self.WIPE_COMMAND = "wipefs -af {0}*"
        else:
            self.WIPE_COMMAND = "wipefs --all --force --no-act {0}*"
    
class RandomOverwriteProcess(ErasureProcess):
    DISPLAY_NAME = "Random Overwrite"

    def __init__(self,drive_model:DriveModel):
        super().__init__(drive_model)
        self.method_name = "Random Overwrite"
        self.compliance = "NIST 800-88 1-Pass"

        if ErasureProcessFactory.WIPE_REAL:
            self.WIPE_COMMAND = "shred -f -n 1 -v {0}"
        else:
            self.WIPE_COMMAND = """echo {0};sleep 1;
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

class NVMeSecureEraseProcess(ErasureProcess):
    DISPLAY_NAME = "NVMe Secure Erase"
    def __init__(self,drive_model:DriveModel):
        super().__init__(drive_model)
        self.method_name = "NVMe Secure Erasure"
        self.compliance = "NIST 800-88 1-Pass"

        if ErasureProcessFactory.WIPE_REAL:
            self.WIPE_COMMAND = "nvme format --force {}"
        else:
            self.WIPE_COMMAND = "echo \"fake nvme wipe {}\""

class ATASecureErasue(ErasureProcess):
    DISPLAY_NAME = "ATA Secure Erasure"

    def __init__(self,drive_model:DriveModel):
        super().__init__(drive_model)
        self.method_name = "ATA Secure Erasure"
        self.compliance = "NIST 800-88 1-Pass"

        if ErasureProcessFactory.WIPE_REAL:
            self.WIPE_COMMAND = "echo error"
        else:
            self.WIPE_COMMAND = "echo Erorr"
