

try:
    import pydevd
    pydevd.settrace(stdoutToServer=True, stderrToServer=True, suspend=False)
except ImportError:
    pass



bl_info = {
    "name": "Import cityGML",
    "author": "Amir and Fahed ",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import City GML file ",
    "warning": "",
    "wiki_url": "",
    "support": 'OFFICIAL',
    "category": "Import-Export",
}


import bpy #blender module give the way to translate, access, definitions of data  ans many ather utilities 
import lxml #traittement du fichier gml 
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Operator
import xml.etree.ElementTree as ET
import bmesh    #gives access the blenders internal mesh editing api, featuring geometry connectivity data 
                #and access to editing operations such as split, separate, collapse and dissolve.
import os

from .building import Building
from .citymodel import CityModel
from .listFile import ListFile
from .polygon import PolyGon
from .texture import Texture




def readDataCityGML(context, filepath, directory, scale):
    
    print("this is your directory", directory)
    firstTime = True
    uc = 0
    lc = 0
    
    listfl = ListFile(directory=directory)
    print(listfl.files)
    
    for file in listfl.files: 
        
        scene = context.scene
        CityGML = ET.parse(directory.replace("\\","/")+"/"+file)# Parsing the file 
        CityGMLroot = CityGML.getroot()#get the root element of the citygml file selected 
        print("Importing CityGML File")
       
    
        if CityGMLroot.tag == "{http://www.opengis.net/citygml/1.0}CityModel":
            
            print("la version de fichier est 1.0")
            #-- Name spaces
            ns_citygml="http://www.opengis.net/citygml/1.0"
    
            ns_gml = "http://www.opengis.net/gml"
            ns_bldg = "http://www.opengis.net/citygml/building/1.0"
            ns_tran = "http://www.opengis.net/citygml/transportation/1.0"
            ns_veg = "http://www.opengis.net/citygml/vegetation/1.0"
            ns_gen = "http://www.opengis.net/citygml/generics/1.0"
            ns_xsi="http://www.w3.org/2001/XMLSchema-instance"
            ns_xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:1.0"
            ns_xlink="http://www.w3.org/1999/xlink"
            ns_dem="http://www.opengis.net/citygml/relief/1.0"
            ns_frn="http://www.opengis.net/citygml/cityfurniture/1.0"
            ns_tun="http://www.opengis.net/citygml/tunnel/1.0"
            ns_wtr="http://www.opengis.net/citygml/waterbody/1.0"
            ns_brid="http://www.opengis.net/citygml/bridge/1.0"
            ns_app="http://www.opengis.net/citygml/appearance/1.0"
            ns_brid="http://www.opengis.net/citygml/bridge/1.0"
        #-- Else probably means 2.0
        else:
            #-- Name spaces
            print("la version de fichier est 2.0")
            ns_citygml="http://www.opengis.net/citygml/2.0"
    
            ns_gml = "http://www.opengis.net/gml"
            ns_bldg = "http://www.opengis.net/citygml/building/2.0"
            ns_tran = "http://www.opengis.net/citygml/transportation/2.0"
            ns_veg = "http://www.opengis.net/citygml/vegetation/2.0"
            ns_gen = "http://www.opengis.net/citygml/generics/2.0"
            ns_xsi="http://www.w3.org/2001/XMLSchema-instance"
            ns_xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
            ns_xlink="http://www.w3.org/1999/xlink"
            ns_dem="http://www.opengis.net/citygml/relief/2.0"
            ns_frn="http://www.opengis.net/citygml/cityfurniture/2.0"
            ns_tun="http://www.opengis.net/citygml/tunnel/2.0"
            ns_wtr="http://www.opengis.net/citygml/waterbody/2.0"
            ns_brid="http://www.opengis.net/citygml/bridge/2.0"
            ns_app="http://www.opengis.net/citygml/appearance/2.0"
            
    
        nsmap = {
        None : ns_citygml,
            'gml': ns_gml,
            'bldg': ns_bldg,
            'tran': ns_tran,
            'veg': ns_veg,
            'gen' : ns_gen,
            'xsi' : ns_xsi,
            'xAL' : ns_xAL,
            'xlink' : ns_xlink,
            'dem' : ns_dem,
            'frn' : ns_frn,
            'tun' : ns_tun,
            'brid': ns_brid,
            'app' : ns_app,
            'wtr': ns_wtr
        }
    
        CityGMLBox = CityGML.find("{%s}boundedBy"%ns_gml)
        name = CityGMLBox.find(".//{%s}Envelope"%ns_gml).attrib["srsName"]
        if firstTime == True: # if the first time we fix the low and aupper corner 
                                # to fix the scal for all file same sacale
            firstTime = False # to use one scalaire 
            uc = CityGMLBox.find(".//{%s}upperCorner"%ns_gml).text
            lc = CityGMLBox.find(".//{%s}lowerCorner"%ns_gml).text
    
        city = CityModel(name=name, upperCorner=uc, lowerCorner=lc)
    
        cityobjects = CityGML.findall("{%s}cityObjectMember"%ns_citygml)
    
    
        for cityobject in cityobjects:
     
            building = cityobject.find("{%s}Building"%ns_bldg) #if building file in parametre 
            
            if building is None:
                building = cityobject.find("{%s}Bridge"%ns_brid) #if bridge file in parametre 
                #print("building", building)
    
            if building is None:
                building = cityobject.find("{%s}GenericCityObject"%ns_gen) #if GenericCityObject file in parametre 
                #print("building", building)
    
     
            if building is None:
                building = cityobject.find("{%s}WaterBody"%ns_wtr) #if water file in paramtre 
                #print("building", building) 
            else:
      
                print("#", end="")
                
            if building :
                
                buildingId = building.attrib["{%s}id" %ns_gml]
        
                rings = cityobject.findall(".//{%s}LinearRing" %ns_gml)
                surfaces = []
                for ring in rings:
                    ringId = ring.attrib["{%s}id"%ns_gml]
                    posList = ring.find("{%s}posList"%ns_gml).text
                    surfaces.append(PolyGon(id=ringId, pts=posList))
            
            
            #to do the relief 
            if building is None : 
                building = cityobject.find("{%s}ReliefFeature"%ns_dem)
                #print("building", building)   
                if building is None:
                    groundSurface = cityobject.find("{%s}GroundSurface"%ns_bldg)
                    print("X",groundSurface, end="")
                    if groundSurface is None:
                        continue
                    building = groundSurface
                else:
                    print("#", end="")
                buildingId = building.attrib["{%s}id" %ns_gml]
        
                rings = cityobject.findall(".//{%s}LinearRing" %ns_gml)
                surfaces = []
                for ring in rings:
                    import random
                    ringId = random.randint(1000, 10000) #ring.attrib["{%s}id"%ns_gml]
                    posList = ring.find("{%s}posList"%ns_gml).text
                    
                    surfaces.append(PolyGon(id=ringId, pts=posList))
                    
                    
            
            textures = []
            sdms = CityGMLroot.findall(".//{%s}surfaceDataMember" %ns_app)
            for sdm in sdms:
                coords = sdm.find(".//{%s}textureCoordinates" %ns_app)
                #print("coooords")
                if coords is None:
                    continue
                sdm_ring = coords.attrib["ring"]
                path = r"%s" % sdm.find(".//{%s}imageURI" %ns_app).text
                
                #print("this is your directory " ,directory+path)
                #print("ring sdm ", sdm_ring)
                textures.append(Texture(id=sdm_ring, map=coords.text, path=(directory+path).replace('\\','/')))
            #buildingId  is the displayed name of the building in Blender 
            
            building = Building(id='buildingId', surfaces=surfaces,textures=textures)
            city.addBuilding(building)
        print()
        print("finished importing, building...")
        city.build(scene, directory, scale)
    print("done")
    return {'FINISHED'}    



class ImportCityGML(Operator, ImportHelper):
    bl_idname = "import_city.gml"
    bl_label = "Import City GML"
    bl_options = {'UNDO', 'PRESET'}

    filename_extention = ".gml"
    filter_glob = StringProperty(default="*.gml",options={'HIDDEN'},)
    directory = StringProperty()
    filepath = StringProperty(name="File Path", description="Filepath used for importing CityGML file",  default= "")


    scale = FloatProperty(
            name="Scale",
            description="Scale the model",
            default=0.09,
            min=0.01,
            max=100.0
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scale")

    def execute(self, context):
        return readDataCityGML(context, self.filepath, self.directory,  self.scale)


def menu_func_import(self, context):
    self.layout.operator(ImportCityGML.bl_idname, text="City GML (.gml)")


def register():
    bpy.utils.register_class(ImportCityGML)
    bpy.types.INFO_MT_file_import.append(menu_func_import) #add import option to import list options 


def unregister():
    bpy.utils.unregister_class(ImportCityGML)
    bpy.types.INFO_MT_file_import.remove(menu_func_import) #delete import option to import list options 


if __name__ == "__main__":
    register()
