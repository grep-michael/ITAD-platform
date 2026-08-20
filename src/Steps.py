from Context import *
import logging

from Erasure.Services.WiperServices import WipeService
from Erasure.Controllers.DriveModel import DriveModel
class WipeStep:
    name = "Wipe Drives"

    def run(self, ctx:Context):
        for storage in ctx.root.findall(".//Storage"):
            model = DriveModel(storage)
            if model.removeable:
                logging.info("%s is removable, skipping",model.name)
                continue
            self.wipe(ctx,model)
    
    def wipe(self,ctx:Context,model:DriveModel):
        logging.info("Wiping drive %s", model.path)
        try:
            service = WipeService(model, None)
            service.start_wipe()
            service._thread.wait(60000)
        except Exception as e:
            ctx.fail(Error(
                Message=f"Erasure failed on {model.path}: {e}",
                Fields=[
                        ErrorField(name="Erasure Error",value=model.path),
                    ]
            ))

from Services.SegmentUploader import *
class APIUploadStep:
    name = "API Uploader"

    def run(self, ctx:Context):
        if ctx.errors:
            return None
        err = SegmentUploader().Upload(ctx.root)
        if err != None:
            ctx.fail(Error(Message=f"API Uploading error: \"{err}\""))

from Services.ShareManager import ShareManager
class ShareUploadStep:
    name = "Share Uploader"

    def run(self,ctx:Context):
        share_manager = ShareManager()

        while not share_manager.mount_share():
            logging.info("Cant connect to share","Failed to connect to share, check internet")
            print("Cant connect to share","Failed to connect to share, check internet")
            time.sleep(5)

        name = ctx.UID if ctx.UID is not None else ctx.serial
        try:
            ok = share_manager.upload_dir("./logs",name)
        finally:
            share_manager.close_share()
        
        if not ok:
            ctx.fail(
                Error(Message="Share Upload Failed")
            )

from Services.FTPManager import *
class FtpUploadStep:
    name = "FTP Uploader"

    def run(self, ctx:Context):
        if not ctx.UID:
            ctx.fail(
                Error(Message="Attempted to upload xml to ftp without uid")
            )
            return 

        files = [ctx.UID, ctx.serial]
        for log in files:
            print("Attempting to upload: ",log)
            ok = FTPUploadStrategy().upload_file("./logs/{}.xml".format(log))
            if ok:
                return 
        ctx.fail(
            Error(Message="Razor ftp Uploader failed")
        )

from Services.NetworkManager import NetworkManager
class SetupNetwork:
    name = "Setup NetWork"

    def run(self, ctx:Context):
        net_manager = NetworkManager()
        net_manager.connect()
        net_manager.refresh_ntpd()
        while not net_manager.can_ping_google():
            print("No internet, attempting reconnect")
            time.sleep(5)
            net_manager.connect()

from Utilities.Marvell.executor import RemoveMarvellRaid
class RemoveRaid:
    name = "Raid Removal"

    def run(self, ctx:Context):
        RemoveMarvellRaid()

from Razor.RazorClient import RazorClient
class SetupRazorClient:
    name = "Razor client setup"

    def run(self, ctx:Context):
        ctx.client = RazorClient()
        err = ctx.client.Login()
        if err != None:
            raise FatalError("Failed to login the Razor Client")

from Utilities.Utils import DeviceScanner
from Services.Parsing.HardwareTreeBuilder import HardwareTreeBuilder
class SetupXML:
    name = "Build XML"
    def run(self, ctx:Context):
        DeviceScanner.create_system_spec_files()
        ctx.root = HardwareTreeBuilder.build_hardware_tree()
        ctx.serial = ctx.root.find(".//System_Serial_Number").text

class GetAsset:
    name = "Get Asset"

    def run(s, ctx:Context):
        if ctx.serial == None or ctx.client == None:
            raise FatalError(f"Attempted to get device by serial but client or serial is None")
        assets, err = ctx.client.Assets.Get().By_Serial(ctx.serial)
        if err != None:
            raise FatalError(f"Failed to get Asset by serial: {err}")
        if len(assets) < 1:
            raise FatalError(f"No asset by serial: {ctx.serial}")
        ctx.asset = assets[0]
        ctx.UID = ctx.asset.uniqueId

from Utilities.Finisher import Finisher
class FinalizeXmlStep:
    name = "Finalizer"

    def run(s,ctx:Context):
        ctx.root.find(".//Unique_Identifier").text = ctx.UID

        Finisher.finialize_process(ctx)#ctx.root,ctx.client,ctx.asset.customer)
        storageCount = len(ctx.root.findall(".//Storage"))
        if storageCount<2:
            ctx.fail(
                Error(
                    Message="Unexpected Storage Count",
                    Fields=[
                        ErrorField(name="Storage Count",value=str(storageCount))
                    ]
                )
            )
        if len(ctx.root.findall(".//Slot_1")) < 1:
            ctx.fail(
                Error(
                    Message="No Network interfaces"
                )
            )
            errorMSG += f"No Network interfaces\n"







