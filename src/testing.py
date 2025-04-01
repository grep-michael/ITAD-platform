from Parsing.XMLBuilders import * 
import xml.etree.ElementTree as ET

XML_TEMPLATE = """
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
</SYSTEM_INVENTORY>
"""



if __name__ == "__main__":
	logging.basicConfig(filename='ITAD_platform.log', level=logging.INFO,filemode="w")
	print("print debugging my beloved")
	template_tree = ET.ElementTree(ET.fromstring(XML_TEMPLATE))
	template_root = template_tree.getroot()

	device_xml_builder = DeviceXMLBuilder()
	devices = device_xml_builder.build_xml_tree(template_root)

	sysinfo_xml_builder = SysInfoXMLBuilder()
	sysinfo = sysinfo_xml_builder.build_xml_tree(template_tree)

	inv = ET.Element("SYSTEM_INVENTORY")
	inv.append(sysinfo);inv.append(devices)

	ET.indent(inv)
	xml_tree = ET.ElementTree(inv)
	xml_tree.write("logs/testing.xml",encoding="utf-8")
