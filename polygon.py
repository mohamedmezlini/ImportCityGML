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




class PolyGon:
    def __init__(self, id="", pts=""):
        def unflatten(coords):
            return [Vector(float(coord) for coord in coords[i:i+3]) for i in range(0, len(coords), 3)] #
        self.id = id
        self.verts = unflatten(pts.split()) # return the list of verts 

