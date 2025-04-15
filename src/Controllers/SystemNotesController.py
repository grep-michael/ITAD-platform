from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADWidget

class SystemNotesController(ITADWidget):
    def __init__(self):
        super().__init__()