import argparse,sys,os


class MainArgParser():
    arguments = {}
    def parse():
        parser = argparse.ArgumentParser(description="ITAD_script")
        parser.add_argument("--env", dest="enviroment", help="path to .env file",default=".env")
        parser.add_argument("--debug", dest="DEBUG", help="path to .env file",default="False")
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

        parser.add_argument('-u', '--uid',type=str)  
        parser.add_argument('-e', '--element',type=str)
        args = parser.parse_args()
        SpecTestingArgParser.arguments = args
        return args
