import bpy
from bpy.types import Operator
from bpy.app.handlers import persistent

import json

from ..parsers import SceneParser
from ..operators.ot_sync import BLIDGE_OT_Sync
from ..utils.json_utils import round_floats


class BLIDGE_OT_GLTFExport(Operator):
    bl_idname = 'blidge.export_gltf'
    bl_label = 'Accept'
    
    @staticmethod
    def export():
        scene = bpy.context.scene
        preset_name = scene.blidge.export_gltf_preset_list

        # https://blenderartists.org/t/using-fbx-export-presets-when-exporting-from-a-script/1162914/2

        if preset_name:
            class Container(object):
                __slots__ = ('__dict__',)

            op = Container()
            with open(preset_name, 'r') as file:
                # storing the values from the preset on the class
                for line in file.readlines()[3::]:
                    exec(line, globals(), locals())

            # set gltf path
            op.filepath = bpy.path.abspath(scene.blidge.export_gltf_path)

            # pass class dictionary to the operator
            kwargs = op.__dict__
            bpy.ops.export_scene.gltf(**kwargs)

            BLIDGE_OT_Sync.ws.broadcast("event", {"type": 'export_gltf'})

    def execute(self, context):
        self.export()
        return {'FINISHED'}

    @classmethod
    @persistent
    def on_save(cls=None, scene: bpy.types.Scene=None):
        scene = bpy.context.scene
        if scene.blidge.export_gltf_export_on_save:
            cls.export()


class BLIDGE_OT_SceneExport(Operator):
    bl_idname = 'blidge.export_scene'
    bl_label = 'Accept'

    def execute(self, context):
        scene = bpy.context.scene
        data = SceneParser().parse_scene()
        path = bpy.path.abspath(scene.blidge.export_scene_data_path)

        # 数値精度を3桁に丸める
        rounded_data = round_floats(data)

        with open(path, mode='wt', encoding='utf-8') as file:
            json.dump(rounded_data, file, ensure_ascii=False, indent=2)

        return {'FINISHED'}

