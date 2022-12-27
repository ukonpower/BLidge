import bpy
from bpy.types import (Operator)

from ..utils.fcurve_manager import get_fcurve_id

class BLIDGE_OT_ObjectUniformCreate(Operator):
    bl_idname = 'blidge.object_uniform_create'
    bl_label="Create Uniform"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        item = bpy.context.scene.blidge.material.uniform_list.add()
        return {'FINISHED'}