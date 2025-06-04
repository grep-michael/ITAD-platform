import subprocess,os,re,logging,argparse,sys
from Utilities.Utils import *
    
def count_by_key_value(dictionary_list, key_name):
    """
    For each dictionary in data_list, return a tuple of (count, original_dict)
    where count is the number of dictionaries with the same value for key_name.
    
    Args:
        data_list: List of dictionaries
        key_name: The key whose values you want to count
        
    Returns:
        List of tuples in the format [(count, original_dict), ...]
    """
    # First count occurrences of each value
    value_counts = {}
    
    for item in dictionary_list:
        if key_name in item:
            value = item[key_name] 
            value_counts[value] = value_counts.get(value, 0) + 1
    
    # Then create the result list
    result = []
    for item in dictionary_list:
        if key_name in item:
            value = item[key_name]
            count = value_counts[value]
            result.append((count, item))
    
    return result

REGEX_ERROR_MSG = "Regex Failed to match"

class ErrorlessRegex():
    def __init__(self):
        self.logger = logging.getLogger("ErrorlessRegex")

    def find(self,pattern,data:str,group:int = 1) -> str:
        """tests pattern against string, returns first group 1 if match, if no match returns REGEX_ERROR_MSG
        Args:
            pattern (regex str): list of patterns to search
            data (str): string to run patterns against
            group (int): group to return, default 1
            
        Returns:
            str: first match
        """
        match = re.search(pattern,data)
        if match:
            #print(match.group(1))
            return match.group(group)
        self.logger.error("find: failed to match regex \"{0}\"".format(pattern))
        return REGEX_ERROR_MSG
    
    def find_first(self,patterns:list,data:str,group:int = 1) -> str:
        """tests patterns against string, returns first group 1 of the first match, if no match returns REGEX_ERROR_MSG
        Args:
            patterns (list): list of patterns to search
            data (str): string to run patterns against
            group (int): group to return, default 1
            
        Returns:
            str: first match
        """
        
        for regex in patterns:
            match = re.search(regex,data)
            if match:
                return match.group(group)
        self.logger.error("find_first: failed to match any regexs \"{0}\"".format(patterns))
        self.logger.error("find_first: data \"{0}\"".format(data))
        return REGEX_ERROR_MSG
    
    def find_all(self,pattern,data:str) -> list:
        """calls re.findall
        Args:
            patterns (str): pattern to find
            data (str): string to run patterns against
            
        Returns:
            list: list of matches, list of REGEX_ERROR_MSG if none found
        """

        matches = re.findall(pattern,data)
        if len(matches) == 0:
            return [REGEX_ERROR_MSG]
        return matches

COMMANDS = {
    "system.txt":["lshw -c system"],
    "cpu.txt":["lshw -c cpu"],
    #"disks.txt":["lshw -c disk"],
    "disks.txt":["lsblk -d -P -o name,model,serial,rota,size,hotplug"],
    "memory.txt":["lshw -c memory"],
    "video.txt":["hwinfo --gfxcard"],
    #"video.txt":["glxinfo | head -n 100"],
    "battery.txt":["upower -i $(upower -e | grep -E '/battery_BAT*')"],
    "usb.txt":["lsusb"],
    "display.txt":["xrandr"],
    "webcam.txt":["fswebcam -r 800x800 --png 0 --save ./specs/webcam.png"], #ristretto webcam.png
    "lspci.txt":["lspci"],
}

DEVICE_LOGGER = logging.getLogger("Utils/DeviceScanner")

class DeviceScanner():
    def create_system_spec_files():
        directory = os.path.join(".", "specs")
        os.makedirs(directory, exist_ok=True)
        for filename,cmd in COMMANDS.items():
            with open(f"./specs/{filename}","w") as f:
                DEVICE_LOGGER.info("generating file {0}".format(filename))
                CommandExecutor.run(cmd,shell=True, stdout=f,stderr=f, text=True)
        CommandExecutor.run(["thunar specs/"],shell=True, text=True)

LOGGER = logging.getLogger("Utils/CommandExecutor")

class CommandExecutor():

    def _LOG(function, cmd,ret, **args):
        LOGGER.info("{0} executed: {1} {2}".format(function, cmd, args))
        LOGGER.info("\n\tSTDOUT --\n\tReturned {0}\n\t-- STDOUT END".format(ret))

    def Popen(cmd,**args):
        ret = subprocess.Popen(cmd,**args)
        CommandExecutor._LOG("Popen", cmd,ret, **args)
        return ret

    def check_call(cmd,**args)->subprocess.CompletedProcess:
        ret = subprocess.check_call(cmd,**args)
        CommandExecutor._LOG("check_call", cmd,ret, **args)
        return ret

    def run(cmd,**args)->subprocess.CompletedProcess:
        ret = subprocess.run(cmd,**args)
        CommandExecutor._LOG("run",cmd,ret, **args)
        return ret
    
    def check_output(cmd,**args)->subprocess.CompletedProcess:
        ret = subprocess.check_output(cmd,**args)
        CommandExecutor._LOG("check_output",cmd, ret,**args)
        return ret
    
PACKAGE_LOGGER = logging.getLogger("Utils/PackageManager")
class PackageManager():
    
    def install_packages():
        print("Installing package...")
        try:
            CommandExecutor.check_call(["installpkg /ITAD_platform/packages/glibc-2.39-x86_64-1.txz"], shell=True, text=True)
            CommandExecutor.check_call(["installpkg /ITAD_platform/packages/fswebcam-20200725-x86_64-1gds.txz"], shell=True, text=True)
            CommandExecutor.check_call(["installpkg /ITAD_platform/packages/libx86emu-3.5-x86_64-1cf.txz"], shell=True, text=True)
            CommandExecutor.check_call(["installpkg /ITAD_platform/packages/hwinfo-23.2-x86_64-1cf.txz"], shell=True, text=True)
        except subprocess.CalledProcessError as e:
            PACKAGE_LOGGER.error("Failed to install packages")
            PACKAGE_LOGGER.error(e)
            print("Failed to install packages, check log")
            exit()
        print("Packages installed\n")