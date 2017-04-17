'''
  
'''

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

from .texture import Texture


class Building:
    def __init__(self, id="", name="", surfaces={},textures={}):
        self.id = id #get the id of building 
        self.name = name #get the name of building 
        self.surfaces = {surface.id: surface for surface in surfaces} #get All surfaces in the bilding         
        self.textures = {texture.id: texture for texture in textures}
        
