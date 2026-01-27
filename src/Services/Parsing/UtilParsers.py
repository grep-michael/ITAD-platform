from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor 
import xml.etree.ElementTree as ET
from datetime import datetime


class ReportInfoPraser():
    def parse(self):
        report_info = ET.Element("Report_Info")
        time = ET.Element("Date")
        time.text = datetime.now().strftime("%-m/%-d/%-Y")
        date = ET.Element("Time")
        date.text = datetime.now().strftime("%-H:%-M:%-S")
        report_info.append(time);report_info.append(date)
        return [report_info]