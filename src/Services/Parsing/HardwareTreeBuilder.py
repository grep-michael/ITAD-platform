from Services.Parsing.XMLBuilders import * 
import xml.etree.ElementTree as ET
from datetime import datetime
XML_TEMPLATE = """
<SYSINFO>
    <SYSTEM_INVENTORY>
        <System_Information>
            <Unique_Identifier></Unique_Identifier> <!--user defined-->
            <Tech_ID></Tech_ID>  <!--user defined-->
            <System_Category></System_Category>  <!--user defined-->
            <System_Chassis_Type></System_Chassis_Type>
            <System_Manufacturer></System_Manufacturer>
            <System_Model></System_Model>
            <System_Serial_Number></System_Serial_Number>
            <OS_Installed>NONE</OS_Installed>  <!--user defined-->
            <Defects_Causing_Failure>N/A</Defects_Causing_Failure>  <!--user defined-->
            <Erasure_Method>NIST-800-88</Erasure_Method>  <!--user defined-->
            <System_Notes></System_Notes>  <!--user defined-->
            <Cosmetic_Grade></Cosmetic_Grade>  <!--user defined-->
            <LCD_Grade></LCD_Grade>  <!--user defined-->
            <Final_Grade></Final_Grade>  <!--user defined-->
        </System_Information>
        <Devices>
            <Webcam></Webcam>
            <Graphics_Controller></Graphics_Controller>
            <Optical_Drive></Optical_Drive>
            <CPU>
                <Family></Family>
                <Model></Model>
                <Speed></Speed>
                <Cores></Cores>
            </CPU>
            <Memory>
                <Slots></Slots>
                <Type></Type>
                <Speed></Speed>
                <Size></Size>
            </Memory>
            <Display>
                <Resolution></Resolution>
                <Size></Size>
            </Display>
            <Battery>
                <Cycles></Cycles> <!--/Apple-->
                <Health></Health>
                <Capacity></Capacity> <!--/mAh for future-proof-->
                <Disposition></Disposition>
            </Battery>
            <Storage_Data_Collection>
                <Count></Count>
                <Serial_Numbers></Serial_Numbers>
                <Models></Models>
                <Sizes></Sizes>
                <Types></Types>
            </Storage_Data_Collection>
            <Storage>
                <Model></Model>
                <Type></Type>
                <Serial_Number></Serial_Number>
                <Erasure_Method></Erasure_Method>
                <Erasure_Results></Erasure_Results>
                <Size></Size>
                <Erasure_Date></Erasure_Date>
            </Storage>	
        </Devices>
        <Report_Info></Report_Info>
    </SYSTEM_INVENTORY>
</SYSINFO>
"""

#XML_BUILDERS = {
#    "System_Information":SysInfoXMLBuilder,
#    "Devices":DeviceXMLBuilder
#}
    

class HardwareTreeBuilder():
    
    
    def build_hardware_tree():
        
        template_tree = ET.ElementTree(ET.fromstring(XML_TEMPLATE))
        template_root = template_tree.getroot()
        xml_builder = XMLBuilder()
        xml_builder.process_tree(template_root)
        ET.indent(template_root)
        template_tree.write('output.xml', encoding='utf-8')
        return template_root


def build_report_info():

    report_info = ET.Element("Report_Info")
    time = ET.Element("Time")
    time.text = datetime.now().strftime("%-m/%-d/%-Y")
    date = ET.Element("Date")
    date.text = datetime.now().strftime("%-H:%-M:%-S")
    report_info.append(time);report_info.append(date)
    return report_info