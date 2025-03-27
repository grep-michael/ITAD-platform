from abc import ABC, abstractmethod
import os,subprocess,time,logging

class FTPConfig():
    FTP_HOST = os.environ["FTP_HOST"]
    FTP_PORT = os.environ["FTP_PORT"]
    FTP_USER = os.environ["FTP_USER"]
    FTP_PASSWORD = os.environ["FTP_PASSWORD"]



class FileUploadStrategy(ABC):
    """
    Abstract base class defining the interface for file upload strategies.
    
    This follows the Strategy Pattern, allowing runtime selection of 
    upload methods without altering the client code.
    ChatGTP generated, human edited
    """
    
    @abstractmethod
    def upload_file(self, 
                    local_file: str, 
                    remote_path: str = None) -> bool:
        """
        Abstract method for uploading a file.
        
        Args:
            local_file (str): Path to the local file to upload
            remote_path (Optional[str]): Optional remote file path
        
        Returns:
            bool: True if upload successful, False otherwise
        """
        pass

class FTPUploadStrategy(FileUploadStrategy):
    """
    Concrete strategy for FTP file uploads using subprocess.
    """
    def __init__(self):
        self.logger = logging.getLogger("FTPUploadStrategy")
    
    def upload_file(self, 
                    local_file: str, 
                    remote_path: str = None) -> bool:
        try:
            # Validate input file exists
            if not os.path.exists(local_file):
                self.logger.error(f"Tried to upload non existant file: {local_file}")
                raise FileNotFoundError(f"Local file not found: {local_file}")
            
            put_command = f"put {local_file}"
            if remote_path:
                put_command += f" {remote_path}"
            
            file_put_segment = "<<< $'{0}'".format(put_command)

            # Construct authentication credentials
            auth = f"{FTPConfig.FTP_USER},{FTPConfig.FTP_PASSWORD}"
            
            # Construct FTP command
            ftp_command = [
                'lftp', 
                '-p',
                str(FTPConfig.FTP_PORT),
                '-u', auth,  # Username and password
                FTPConfig.FTP_HOST,
                file_put_segment
            ]
            
            cmd = ' '.join(ftp_command)
            
            # Run FTP upload process
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True,
                executable='/bin/bash' #Bash is needed for the <<< redirect
            )
            self.logger.info(process)
            # Check for successful upload
            return process.returncode == 0
        
        except Exception as e:
            self.logger.error(f"FTP failed: {e}")
            print(f"FTP Upload Error: {e}")
            return False