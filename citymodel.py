

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
from .texture import Texture
from numpy._distributor_init import path
from pathlib import Path


#Envelope defines an extent using a pair of positions defining opposite corners in arbitrary dimensions. The first direct position is the 
#"lower corner" (a coordinate position consisting of all the minimal ordinates for each dimension for all points within the envelope)
#the second one the 
#"upper corner" (a coordinate position consisting of all the maximal ordinates for each dimension for all points within the envelope).
class CityModel:
    def __init__(self, name="", upperCorner="", lowerCorner=""):
        self.lowerCorner = Vector(float(x) for x in lowerCorner.split())
        self.upperCorner = Vector(float(x) for x in upperCorner.split())
        self.name = name
        self.buildings = {}

    def addBuilding(self, building):
        self.buildings[building.id] = building

    def build(self, scene, filepath, scale):
        
        #
        for cityObjectMemberId, building in self.buildings.items():
            #print("City Object Member Id ", cityObjectMemberId ,"   ",  )
            verts_get = []
            bMesh = bmesh.new() # create an empty BMesh
            bMesh.verts.ensure_lookup_table() #Ensure internal data needed for int subscription is initialized with verts/edges/faces, eg bm.verts[index].
                                              #This needs to be called again after adding/removing data in this sequence.
            mesh = bpy.data.meshes.new(building.id) #assign the building.id to the mesh 

            for surfaceId, surface in building.surfaces.items():
                verts = [bMesh.verts.new(scale * (vert - self.lowerCorner)) for vert in surface.verts]
                if (verts.__len__()>2):
                    face = bMesh.faces.new(verts)    
                    #print("ill do the texture now ")              
                    texture = building.textures.get("#%s" %surface.id)
                    if texture:                    
                        uv_layer = bMesh.loops.layers.uv.verify()
                        tex = bMesh.faces.layers.tex.verify()
                        bMesh.faces.ensure_lookup_table()
                        for i,l in enumerate(bMesh.faces[-1].loops):
                            uv = l[uv_layer].uv
                            (uv.x, uv.y) = texture.map[i]
    
                        path = os.path.join(filepath, texture.path)
                        
                        image = bpy.data.images.get(os.path.basename(path))
                        #print("image path after refractor ", path)
                        if not image:
                            image = bpy.data.images.load(path)
                            image.use_fake_user = True  
                            
                        bMesh.faces[-1][tex].image = image  
                        dubs = bmesh.ops.find_doubles(bMesh, verts=verts, dist=0.001)['targetmap']
                        if len(dubs.keys()) > 2:
                            verts_get.extend(dubs.values())

                
                
            verts = list(set(bMesh.verts) - set(verts_get)) # get the list of verts 
            ##bmesh.ops.remove_doubles(bMesh, verts=verts, dist=0.001)
            #bmesh.ops.automerge(bMesh, verts=bMesh.verts, dist=0.000001)
            bMesh.to_mesh(mesh)
            building = bpy.data.objects.new(building.id, mesh)# create new object and add it to mesh 
            scene.objects.link(building) # link the object to the present scene 
            bMesh.free() 


