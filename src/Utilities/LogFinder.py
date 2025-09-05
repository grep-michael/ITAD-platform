import pathlib,logging

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
            
            selection_text = input(">>")

            try:
                selection = int(selection_text)
            except:
                logging.info("FAILED TO CONVERT TO INT")
                print("INPUT FAILED TO BE CONVERTED TO NUMBER")
                print(f"INPUT: {selection_text}")
                
                xml_logs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                selection = 0
                print(f"USING DEFAULT: {xml_logs[selection].name}")
                
        uuid = xml_logs[selection].name.split(".")[0]
        return uuid

if __name__ == "__main__":
    lg = LogFinder()
    uuid = lg.find_uuid()
    print(uuid)