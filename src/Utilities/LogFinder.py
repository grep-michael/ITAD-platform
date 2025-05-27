import pathlib

class LogFinder():
    def __init__(self):
        pass
    

    def find_uuid(self):
        xml_logs = list(pathlib.Path("./logs").glob("*.xml"))
        selection = 0
        if len(xml_logs) > 1:
            print("Multiple XML logs detected, select one")
            for i,log in enumerate(xml_logs):
                print("{} - {}".format(i,log.name))
            selection = int(input(">>"))
        uuid = xml_logs[selection].name.split(".")[0]
        return uuid