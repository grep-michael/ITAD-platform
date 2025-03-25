
import xml.etree.ElementTree as ET
import os,re,json

class DataRefiner():
    pass



class LogConfig():
    TXT_HEADER = "\n"*2+"="*8 + "{}" + "="*8+"\n"*2

class LogCondensor():
    def __init__(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def condense_logs(self):
        raise NotImplementedError()
    
    def get_data(self,file):
        raise NotImplementedError()
    
    def format_master_log(self,files:dict,containter:str="{}",seperator:str="",header:str="") -> str:
        master_str = []
        for filename,contents in files.items():
            entry_str = header.format(filename)
            entry_str += str(contents)
            master_str.append(entry_str)
        return containter.format(seperator.join(master_str))

    def read_logs(self,directory,file_regex=r".*"):
        files_dict = {}
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                matches = bool(re.match(file_regex,filename))
                if matches:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        files_dict[filename] = self.get_data(file)
        return files_dict


class SpecCondensor(LogCondensor):
    def __init__(self):
        super().__init__()
        self.file_regex = r".*\.txt"
        self.directory = "specs/"
        self.header = LogConfig.TXT_HEADER

    def condense_logs(self):
        files = self.read_logs(self.directory,self.file_regex)
        master_log_str = self.format_master_log(files,header=self.header)
        
        with open("logs/system_specs.txt","w") as f:
            f.write(master_log_str)
        
    def get_data(self, file):
        return file.read()

class ErasureCondensor(LogCondensor):
    def __init__(self):
        super().__init__()
        self.file_regex = r".*\.json"
        self.directory = "specs/erasures"
        self.container = "[{}]"
        self.seperator = ","
    
    def _replace_python_with_json(self,byte_array):
        byte_array = byte_array.replace(b"'",b'"')
        byte_array = byte_array.replace(b"True",b"true")
        byte_array = byte_array.replace(b"False",b"false")
        byte_array = byte_array.replace(b"None",b"null")
        return byte_array

    def condense_logs(self):
        files = self.read_logs(self.directory,self.file_regex)
        master_log_str = self.format_master_log(files,containter=self.container,seperator=self.seperator)
        master_bytes = master_log_str.encode('utf-8')
        master_bytes = self._replace_python_with_json(master_bytes)


        #this is retarded but it works :)
        with open("logs/erasure.json","wb+") as f:
            f.write(master_bytes)
            #write bytes
        with open("logs/erasure.json", 'r') as file:
            data = json.load(file)
            #read json
        with open("logs/erasure.json", 'w') as file:
            json.dump(data, file, indent=4)
            #format json
    
    def get_data(self, file):
        return json.load(file)