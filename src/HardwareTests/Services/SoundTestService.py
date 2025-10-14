import subprocess

class SoundTestService():
    
    def __init__(self):
        #start pulse audio
        check = subprocess.run(["pulseaudio --check"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        if check.returncode == 0: #pulse audio is already running
            subprocess.run(["pulseaudio --kill"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        
        start = subprocess.run(["pulseaudio --start"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        if start.returncode != 0:
            subprocess.Popen(["pulseaudio --system"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

    def beep(self):
        subprocess.run(["paplay /ITAD_platform/assets/startup.mp3"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
