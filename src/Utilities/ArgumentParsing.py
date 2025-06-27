import argparse,sys,os

def process_list(arg):
    accepted = ["connect","dump","confirm","upload"]
    args = arg.split(',')
    for i in args:
        if i not in accepted:
            raise argparse.ArgumentTypeError(f"invalid choice: \"{i}\" (choose from {', '.join(accepted)})")
    return args




class MainArgParser():
    arguments = {}

    def parse():
        parser = argparse.ArgumentParser(description="ITAD_script")
        parser.add_argument("--env", dest="enviroment", help="path to .env file",default=".env")
        parser.add_argument("--debug", dest="DEBUG", help="bool for debugging",default="False",choices={"False","True"})
        parser.add_argument("--upload", dest="UPLOAD_TO_SHARE", help="bool for uploading",default="True",choices={"False","True"})
        parser.add_argument("--process",dest="process",
                            help="List of process to take on a system\noptions are [connect,dump,confirm,upload]",
                            type=process_list,
                            default=["connect","dump","confirm","upload"])
        args = parser.parse_args()
        MainArgParser.arguments = args
        return args
    

class SpecTestingArgParser():
    arguments = {}
    def parse():
        parser = argparse.ArgumentParser(
                    prog='spec tester',
                    description='Downloads all spec files and parses them using the current parsers, then compares the results to the actual xml stored on the share',
                    epilog='wagagabagabobo')

        parser.add_argument('-u', '--uid',help="individual uid to download",type=str)  
        parser.add_argument('-e', '--element',help="specific element tag to check for changes on",type=str)
        parser.add_argument('-f', '--filename',help="File list of uids to download and test on",type=str)
        args = parser.parse_args()
        SpecTestingArgParser.arguments = args
        return args
