import argparse
parser = argparse.ArgumentParser(description="ITAD_script")
parser.add_argument("--env", dest="enviroment", help="path to .env file")
args = parser.parse_args()
print(args.enviroment)