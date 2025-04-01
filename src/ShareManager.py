from Utilities.Utils import load_env_file
load_env_file()

import os,subprocess,logging,datetime


class ShareConfig():
    # "mount -t cifs  -o username=guest,password= //10.1.4.128/share /mnt/network_drive"
    TYPE = "cifs"
    MOUNT_LOCATION = "/mnt/shared_space"
    IP = os.environ["SHARE_IP"]
    SHARE_NAME = os.environ["SHARE_NAME"]
    SHARE_DIRECTORY = "/Asset\ Reports/" #spaces have to be backslashed for linux commands
    USER = os.environ["SHARE_USER"]
    PASSWORD = os.environ["SHARE_PASSWORD"]

    def Generate_Mount_Command():
        return "sudo mount -t {0} -o username={1},password={2} //{3}/{4} {5}".format(
            ShareConfig.TYPE,
            ShareConfig.USER,
            ShareConfig.PASSWORD,
            ShareConfig.IP,
            ShareConfig.SHARE_NAME,
            ShareConfig.MOUNT_LOCATION
        )
    
    def Generate_Friendly_Share_Name():
        return "//{0}/{1}".format(ShareConfig.IP,ShareConfig.SHARE_NAME)

class SharedFolder(ShareConfig):
    def __init__(self):
        self.mount_command = ShareConfig.Generate_Mount_Command()

    def mount(self) -> bool:
        """
        Return:
            bool: true if the mount of successfull
        """
        mount_ret = subprocess.run(self.mount_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        return mount_ret.returncode == 0

    def unmount(self):
        umount_ret = subprocess.run("sudo umount {}".format(ShareConfig.MOUNT_LOCATION),stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

class ShareManager():
    def __init__(self):
        self.share = SharedFolder()
        self.logger = logging.getLogger("ShareManager")
        self.base_dir = ShareConfig.MOUNT_LOCATION + ShareConfig.SHARE_DIRECTORY
    
    def _copy_from_share_command(self,remote,local):
        return "cp -r {0} {1}".format(self.base_dir+remote,local)

    def clear_collisions(self,file:str):
        pyFile = file.replace("\\","")
        if os.path.exists(pyFile):
            self.logger.info("Collision found: {}".format(pyFile))
            filename = file.split("/")[-1] + "_" + datetime.datetime.now().strftime("%H-%M-%S:%m-%d-%Y")
            path = '/'.join(file.split("/")[:-1])
            new_file = path + "/" + filename
            command = "sudo mv {} {}".format(file,new_file)
            ret = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            self.logger.info("Collision removed: {}".format(ret))

    def _copy_to_share_command(self,folder,alternative_name):
        command = "sudo cp -r {1} {0}".format(self.base_dir+alternative_name,folder)
        return command

    def download_dir(self,remote_directory,local_directory):
        command = self._copy_from_share_command(remote_directory,local_directory)
        copy_ret = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        return copy_ret.returncode == 1

    def upload_dir(self,direcotry:str,alternative_name=""):
        self.logger.info("Uploading {}".format(direcotry))
        self.clear_collisions(self.base_dir+alternative_name)
        command = self._copy_to_share_command(direcotry,alternative_name)
        copy_ret = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        return copy_ret.returncode == 1

    def mount_share(self):
        if os.path.isdir(ShareConfig.MOUNT_LOCATION):
            self.logger.info("Mounting share: {}".format(ShareConfig.Generate_Friendly_Share_Name()))
            if self.share.mount():
                self.logger.info("Mount Successfull")
            else:
                self.logger.info("Mounting Failed")
        else:
            self.logger.warning("Mount location not found, making directory: {}".format(ShareConfig.MOUNT_LOCATION))
            os.mkdir(ShareConfig.MOUNT_LOCATION)
            self.mount_share()
    
    def close_share(self):
        self.share.unmount()

if __name__ == "__main__":
    logging.basicConfig(filename='ShareManager.log', level=logging.INFO,filemode="w")
    
    #share_manager = ShareManager()
    #share_manager.mount_share()
    #share_manager.upload_dir("./logs","logName")
    #share_manager.download_dir("logName",".")
    #share_manager.close_share()
