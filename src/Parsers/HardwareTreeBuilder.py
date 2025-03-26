from Parsers.DeviceParser import *
from Parsers.SystemInfoParser import *
import xml.etree.ElementTree as ET


XML_TEMPLATE = """
<SYSTEM_INVENTORY>
    <System_Information>
        <Unique_Identifier>Default UUID</Unique_Identifier> <!--user defined-->
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
</SYSTEM_INVENTORY>
"""

PARSER_TABLE = {
    "System_Information":SystemInfoParser,
    "Devices":DeviceParser
}
    

class HardwareTreeBuilder():
    
    
    def build_hardware_tree():
        root = ET.Element("SYSINFO")
        sys_inventory = ET.Element("SYSTEM_INVENTORY")

        
        tree = ET.ElementTree(ET.fromstring(XML_TEMPLATE))
        template = tree.getroot()
        for index,child in enumerate(template):
            try:
                xml = PARSER_TABLE[child.tag](child).build_xml_tree()
                sys_inventory.append(xml)
            except KeyError:
                print("func build_hardware_tree: {0} not found in PARSE_TABLE".format(child.tag))


        root.append(sys_inventory)
        return root