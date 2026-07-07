from Utilities.discord_noitification import *
from Utilities.Config import ConfigLoader,Config
from Utilities.discord_noitification import *

if __name__ == "__main__":
    ConfigLoader.init()
    SendDiscordSuccess("Test","Test message",[{"name": "test", "value": "Field"}])