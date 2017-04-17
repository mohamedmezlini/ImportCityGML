'''
this class return a list of file with the os Directory 
'''



import os
class ListFile:
    def __init__(self, directory = ""):
        self.files = [ file for file in os.listdir(directory.replace("\\","/"))  if file.endswith(".gml") ]
