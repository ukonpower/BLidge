import bpy
from bpy.types import (Operator)

from ..utils.fcurve_manager import get_fcurve_id
from ..globals.properties import (BLidgeObjectProperty)

class BLIDGE_OT_ObjectUniformCreate(Operator):
    bl_idname = 'blidge.object_uniform_create'
    bl_label="Create Uniform"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        object = context.object
        item = object.blidge.material.uniform_list.add()

        return {'FINISHED'}