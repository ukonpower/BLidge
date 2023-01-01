import bpy
from bpy.types import (Operator)

class BLIDGE_OT_ObjectUniformCreate(Operator):
    bl_idname = 'blidge.object_uniform_create'
    bl_label="Create Uniform"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        object = context.object
        item = object.blidge.material.uniform_list.add()
        item.name = '<name>'

        return {'FINISHED'}



class BLIDGE_OT_ObjectUniformRemove(Operator):
    bl_idname = 'blidge.object_uniform_remove'
    bl_label="Remove Uniform"
    bl_options = {'REGISTER', 'UNDO'}
        
    item_index: bpy.props.IntProperty(default=0)

    def execute(self, context): 
        object = context.object
        object.blidge.material.uniform_list.remove(self.item_index)
        
        return {'FINISHED'}