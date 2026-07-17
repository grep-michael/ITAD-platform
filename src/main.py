import logging,os
from Utilities.Config import ConfigLoader,Config
ConfigLoader.init()
if not os.path.exists("./logs/"):
    os.mkdir("./logs/")
logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")
logging.info(Config.VERSION)

import Steps as steps
from Pipeline import *

def main():
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
        steps.ShareUploadStep()
    ])

    pipeline.run(Context())


if __name__ == "__main__":
    main()