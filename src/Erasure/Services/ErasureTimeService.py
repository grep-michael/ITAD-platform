from Erasure.Views.DriveItemView import DriveItemView,SatusBox
from Erasure.Messages import *
from datetime import datetime,timedelta
import re

class TimeService():
    def __init__(self):
        pass

    def connect_to_view(self,view:SatusBox):
        self.view:SatusBox = view

    def update_esitmate(self):
        time_diff = self.current_percentage_time - self.last_percentage_time
        percentage_diff = self.current_percentage - self.last_percentage
        
        progress_rate = percentage_diff / time_diff.total_seconds()

        remaining_precent = 100 - self.current_percentage
        remaining_time = remaining_precent / progress_rate
        
        est_time = self.current_percentage_time + timedelta(seconds=remaining_time)
        self.view.time_estimate.setText(est_time.strftime("%I:%M %p"))

    def find_percentage(self,message:ErasureStatusUpdateMessage):
        match = re.search(r"(\d{1,2})%",message.message)
        if match == None: return
        try:
            percent = int(match.group(1))
            
            if hasattr(self,"last_percentage"):
                if percent <= self.last_percentage: return

                self.current_percentage = percent
                self.current_percentage_time = datetime.now() 
                self.update_esitmate()


            self.last_percentage = percent
            self.last_percentage_time = datetime.now()
            
        except Exception as e:
            #idk
            print(e)
            return 


    def start_timer(self):
        self.view.start_time.setText(datetime.now().strftime("%I:%M %p"))
        self.raw_start_time = datetime.now()
        
    def update_timer(self):
        if not hasattr(self,"raw_start_time"):
            return
        seconds_passed = (datetime.now() - self.raw_start_time).total_seconds()
        hours, remainder = divmod(seconds_passed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.view.time_elasped.setText('{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)))