import subprocess
from Utilities.Config import *

class Command():
    def __init__(self):
        self.args = {
                "shell":True,
                "stdout":subprocess.PIPE,
                "stderr":subprocess.STDOUT,
                "text":True,
        }
        self.command:str
        self.executor:callable


