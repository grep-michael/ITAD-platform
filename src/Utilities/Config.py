import os,sys,argparse
from Utilities.ArgumentParsing import MainArgParser
from Utilities.ArgumentParsing import SpecTestingArgParser

class Config(argparse.Namespace):
    SHARE_IP:str
    SHARE_NAME:str
    SHARE_DIR:str = ""
    SHARE_USER:str
    SHARE_PASSWORD:str
    VERSION:str
    WIFI_SSID:str
    WIFI_PASSWORD:str
    FTP_HOST:str
    FTP_PORT:str
    FTP_USER:str
    FTP_PASSWORD:str
    DEBUG:str
    UPLOAD_TO_SHARE:str
    OPERATOR_PREFIX:str
    OPERATOR_COUNT:str
    process:list
    TIME_ZONE:set


class ConfigLoader:
    arguments:argparse.Namespace
    enviroment_varibles:dict = {}
    def init():
        ConfigLoader.arguments = MainArgParser.parse()
        load_argparser_Namespace_into_config(ConfigLoader.arguments)
        load_env_into_config(ConfigLoader.arguments.enviroment)

    def init_spec_testing():
        ConfigLoader.arguments = SpecTestingArgParser.parse()
        load_argparser_Namespace_into_config(ConfigLoader.arguments)
        load_env_into_config()

def load_argparser_Namespace_into_config(namespace):
    for i,k in namespace.__dict__.items():
        setattr(Config,
                i,
                k)

def load_env_into_config(filepath=".env"):
    env_vars = {}
    
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    if "LOADED_FROM_SCRIPT" not in env_vars.keys():
        #prevent loading the env multiple times, not needed but I like having it just in case 
        env_vars["LOADED_FROM_SCRIPT"] = "1"
        for key, value in env_vars.items():
            setattr(Config,
                    key,
                    value)
            
            #os.environ[key] = value