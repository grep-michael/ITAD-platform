from AttributeGathering.Controllers.BasicNodeController import BasicNodeController
from AttributeGathering.Views.WebcamView import WebCamView
import xml.etree.ElementTree as ET
import subprocess

class WebcamController(BasicNodeController):
    def __init__(self, element:ET.Element):
        super().__init__(element)
        self.find_video_sources()
        self.view:WebCamView
    
    def connect_view(self, view:WebCamView):
        super().connect_view(view)

        self.view.retake_button.clicked.connect(self.handle_retake_request)
        self.view.video_selector.currentIndexChanged.connect(self.handle_selected_video_change)
        
        self.view.video_selector.addItems(self.video_options)
    
    def find_video_sources(self):
        video_streams = subprocess.run(["find /dev/video*"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        self.video_options = video_streams.stdout.decode().strip().split('\n')
    
    def handle_selected_video_change(self,index:int):
        item = self.view.video_selector.itemText(index)
        self.selected_vidoe_source = item

    def handle_retake_request(self):
        
        command = "fswebcam -r 800x800 --png 0 --save ./specs/webcam.png --device {}".format(self.selected_vidoe_source)
        fscam = subprocess.run([command],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        print(fscam)
        self.view.update_png()

    