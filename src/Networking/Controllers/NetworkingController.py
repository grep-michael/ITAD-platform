
from Generics import ITADController
from Networking.Views.NetworkingView import NetworkingView

class NetworkingController(ITADController):
    
    def __init__(self,Element):
        #Element is ignored, its only used for that ControllerFactory 
        super().__init__()
    
    def connect_view(self, view:NetworkingView):
        self.view:NetworkingView = view
        
