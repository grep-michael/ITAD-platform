from Utilities.Config import *
from Services.Commands.Command import *

class PartitionHeaderEraseCommand(Command):
    def __init__(self):
        super().__init__()
        if Config.DEBUG == "False":
            self.WIPE_COMMAND = "wipefs -af {0}*"
        else:
            self.WIPE_COMMAND = "wipefs --all --force --no-act {0}*"

class RandomOverwriteEraseCommand(Command):
    def __init__(self):
        super().__init__()
        if Config.DEBUG == "False":
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

class NVMESecureEraseCommand(Command):
    def __init__(self):
        super().__init__()

        if Config.DEBUG == "False":
            self.WIPE_COMMAND = "nvme format --force {}"
        else:
            self.WIPE_COMMAND = "echo \"fake nvme wipe {}\""

class ATASecureEraseCommand(Command):
        
    def __init__(self):
        super().__init__()
        self.executor = subprocess.Popen

        self.args = {
            "shell":True,
            "stdout":subprocess.PIPE,
            "stderr":subprocess.STDOUT,
            "text":True,
            "executable":"/bin/bash"
        }

        if Config.DEBUG == "False":
            self.command = """
            hdparm --yes-i-know-what-i-am-doing --sanitize-block-erase "{0}";
            error=$?; 
            if [ $error -ne 0 ]; then exit $error; fi;
            status="In Process";
            while [[ "$status" == *"In Process"* ]]; do 
                status=$(hdparm --sanitize-status "{0}" 2>&1); 
                echo $status | sed -E "s/(\/dev\/sd\w).*status:(.*)/\\1 \\2/";
                sleep 3;
            done"""
        else:
            self.command = """echo "/dev/sdb  State: SD2 Sanitize operation In Process Progress: 0x1e (0%)";sleep 3;
    echo "/fakeDrive  State: SD2 Sanitize operation In Process Progress: 0x2ee8 (18%)";sleep 3;
    echo "/fakeDrive  State: SD2 Sanitize operation In Process Progress: 0x5fa5 (37%)";sleep 3;
    echo "/fakeDrive  State: SD2 Sanitize operation In Process Progress: 0x8e11 (55%)";sleep 3;
    echo "/fakeDrive  State: SD2 Sanitize operation In Process Progress: 0xbb27 (73%)";sleep 3;
    echo "/fakeDrive  State: SD2 Sanitize operation In Process Progress: 0xe899 (90%)";sleep 3;
    echo "/fakeDrive  State: SD0 Sanitize Idle Last Sanitize Operation Completed Without Error"
    """