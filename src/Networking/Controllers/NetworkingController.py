
from Generics import ITADController
from Networking.Views.NetworkingView import NetworkingView
from PyQt5.QtCore import pyqtSlot,pyqtSignal
from Services.NetworkManager import NetworkManager
import sys,io
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QObject,QThread,QProcess

class NetworkingController(ITADController):
    
    def __init__(self,Element):
        #Element is ignored, its only used for that ControllerFactory 
        #element is however the root element of our xml tree so we could use it if we wanted
        super().__init__()
        self.original_out = sys.stdout
        sys.og_out = sys.stdout
        
    
    def connect_view(self, view:NetworkingView):
        self.view:NetworkingView = view
        self.view.signal_onshow.connect(self.show_event)
        self.view.quit_button.clicked.connect(self.interrupt_worker)


    def show_event(self):
        print("show")
        

        self._thread = QThread()
        self.worker = Worker(self.view.status)
        self.worker.moveToThread(self._thread)

        self._thread.started.connect(self.worker.run)
        self._thread.finished.connect(self.worker_finished)

        self._thread.start()
            
    def worker_finished(self):
        self._thread.deleteLater()
        #self.view.status.setText("Network manager finished")
        print("done")
        

class Worker(QObject):
    def __init__(self,label):
        super().__init__()
        self.label = label
        self.net_manager = NetworkManager()
        self.original_out = sys.stdout
        self.interrupt = False

    def slot_interrupt(self):
        self.interrupt = False
    
    def is_

    @pyqtSlot()
    def run(self):
        string_buffer = PrintRedirector(self.label)
        sys.stdout = string_buffer
        
        try:
            self.net_manager.test(self.interrupt)
            #self.net_manager.connect()
            #self.net_manager.refresh_ntpd(self.interrupt)
        except Exception as e:
            print(e)
        finally:
            self.finish_work()
    
    def finish_work(self):
        sys.stdout = self.original_out
        print("Finishing work")
        self.deleteLater()
        self.thread().exit()



        
class PrintRedirector(QObject):

    def __init__(self,label):
        super().__init__()
        self.label:QLabel = label

    def write(self, text):
        if text.strip():  # ignore empty lines from print()
            self.label.setText(text)

    def flush(self):
        pass