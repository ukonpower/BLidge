import bpy
import json

from bpy.types import (Operator)

from ..utils.scene_parser import SceneParser

class BLIDGE_OT_ExportSceneData(Operator):
    bl_idname = 'blidge.export_scene'
    bl_label = 'Accept'
    
    def execute(self, context):
        scene = bpy.context.scene
        data = SceneParser().get_scene()
        path = scene.blidge.export_scene_data_path

        with open( path, mode='wt', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
            
        return {'FINISHED'}

