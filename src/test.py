from Utilities.discord_noitification import *
from Utilities.Config import ConfigLoader,Config
from Utilities.discord_noitification import *
from Razor.RazorClient import RazorClient

if __name__ == "__main__":
    ConfigLoader.init()
    client = RazorClient()
    err = client.Login()
    if err != None:
        SendDiscordError("Failed to login",err)
    else:
        SendDiscordSuccess("Login Success","")