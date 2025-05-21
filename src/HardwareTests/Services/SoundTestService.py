import subprocess

class SoundTestService():
    
    def __init__(self):
        #start pulse audio
        subprocess.run(["/etc/rc.d/rc.pulseaudio start"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    
    def beep(self):
        subprocess.run(["aplay /usr/share/wav/beep_05.wav"],stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
