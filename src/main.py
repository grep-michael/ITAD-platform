import logging,os
from Utilities.Config import ConfigLoader,Config
ConfigLoader.init()
if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

#basic logging
logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")
logging.info(Config.VERSION)

#api logging
request_logger = logging.getLogger("razor.api")
request_logger.setLevel(logging.INFO)
_handler = logging.FileHandler("./logs/requests.log", mode="w")
_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
request_logger.addHandler(_handler)
request_logger.propagate = False


import Steps as steps
from Pipeline import *

def main():
    context = Context()
    try:
        pipeline = Pipeline([
            steps.SetupNetwork(),
            steps.RemoveRaid(),
            steps.SetupRazorClient(),
            steps.SetupXML(),
            steps.GetAsset(),
            steps.WipeStep(),
            steps.FinalizeXmlStep(),
            steps.APIUploadStep(),
            steps.FtpUploadStep(),
        ])
        pipeline.run(context)
    finally:
        uploadStep = steps.ShareUploadStep()
        uploadStep.run(context)


if __name__ == "__main__":
    main()