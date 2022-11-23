import bpy

# sync

from ..operators.sync import (BLIDGE_OT_Sync)

# exports

from ..operators.export_gltf import (BLIDGE_OT_ExportGLTF)
from ..operators.export_scene_data import (BLIDGE_OT_ExportSceneData)

class BLIDGE_PT_MainControls(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BLidge'

    def draw(self, context):
        scene = context.scene
        # sync
        syncCls = BLIDGE_OT_Sync
        layout = self.layout
        layout.label(text='Sync')
        col = layout.column()
        col.prop(scene.blidge,'sync_port', text='port')
        if syncCls.is_running():
            col.enabled = False
            layout.operator(syncCls.bl_idname, text='Syncing...', icon='PAUSE', depress=True)
        else:
            col.enabled = True
            layout.operator(syncCls.bl_idname, text='Sync', icon='PLAY')
        layout.separator()

        # gltf
        layout.label(text='glTF')
        layout.prop(scene.blidge,'export_gltf_export_on_save', text='export on save')
        layout.prop(scene.blidge,'export_gltf_preset_list', text='preset')

        layout.prop( scene.blidge, 'export_gltf_path' )
        layout.operator(BLIDGE_OT_ExportGLTF.bl_idname, text='Export glTF (glb)' )

        # sceneData
        layout.label(text='Scene data')
        layout.prop( scene.blidge, 'export_scene_data_path' )
        layout.operator(BLIDGE_OT_ExportSceneData.bl_idname, text='Export scene data' )