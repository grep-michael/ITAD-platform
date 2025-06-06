from Services.DataRefiner import *

class Finisher():
    
    def finialize_process(root):
        LogRefiner.Refine_data()
        XMLTreeRefiner.Refine_tree(root)

