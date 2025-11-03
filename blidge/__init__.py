bl_info = {
    "name" : "blidge",
    "author" : "ukonpower",
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Testing"
}


if "bpy" in locals():
    import imp
    imp.reload(BLidgeProperties)
    imp.reload(BLIDGE_OT_install_dependencies)
    imp.reload(BLIDGE_PT_install_dependencies)
    imp.reload(BLIDGE_OT_GLTFExport)
    imp.reload(BLIDGE_OT_SceneExport)
    imp.reload(BLIDGE_OT_Sync)
    imp.reload(BLIDGE_OT_AddCustomProperty)
    imp.reload(BLIDGE_OT_RemoveCustomProperty)
    imp.reload(BLIDGE_OT_ObjectUniformCreate)
    imp.reload(BLIDGE_OT_ObjectUniformRemove)
    imp.reload(BLIDGE_OT_ObjectAnimationCreate)
    imp.reload(BLIDGE_OT_ObjectAnimationRemove)
    imp.reload(BLIDGE_OT_ObjectAnimationToggleUniform)
    imp.reload(BLIDGE_OT_AddFCurveToAnimation)
    imp.reload(BLIDGE_OT_FCurveMapperCreate)
    imp.reload(BLIDGE_OT_FCurveSetAnimationID)
    imp.reload(BLIDGE_OT_FCurveMapperClear)
    imp.reload(BLIDGE_OT_FCurveMapperAdd)
    imp.reload(BLIDGE_OT_FCurveMapperRemove)
    imp.reload(BLIDGE_OT_FCurveMapperChange)
    imp.reload(BLIDGE_PT_Controls)
    imp.reload(BLIDGE_PT_ObjectPropertie)
    imp.reload(BLIDGE_PT_FCurveMapper)
    imp.reload(BLidgeVirtualMeshRenderer)
else:
    import bpy
    from .globals.config import Globals
    from .globals.properties import BLidgeProperties
    from .globals.preference import BLIDGE_OT_install_dependencies, BLIDGE_PT_install_dependencies
    from .operators.ot_export import BLIDGE_OT_GLTFExport, BLIDGE_OT_SceneExport
    from .operators.ot_sync import BLIDGE_OT_Sync
    from .operators.ot_fcurve import BLIDGE_OT_FCurveMapperCreate, BLIDGE_OT_FCurveSetAnimationID, BLIDGE_OT_FCurveMapperClear, BLIDGE_OT_FCurveMapperAdd, BLIDGE_OT_FCurveMapperRemove, BLIDGE_OT_FCurveMapperChange
    from .operators.ot_object import BLIDGE_OT_AddCustomProperty, BLIDGE_OT_RemoveCustomProperty, BLIDGE_OT_ObjectUniformCreate, BLIDGE_OT_ObjectUniformRemove, BLIDGE_OT_ObjectAnimationCreate, BLIDGE_OT_ObjectAnimationRemove, BLIDGE_OT_ObjectAnimationToggleUniform, BLIDGE_OT_AddFCurveToAnimation
    from .panels.pt_view_controls import BLIDGE_PT_Controls
    from .panels.pt_prop_object import BLIDGE_PT_ObjectPropertie
    from .panels.pt_graph_fcurve import BLIDGE_PT_FCurveMapper
    from .renderer.renderer_virtual_mesh import BLidgeVirtualMeshRenderer
    from .globals.events import register_event, unregister_event

classes = [
    BLIDGE_OT_GLTFExport,
    BLIDGE_OT_SceneExport,
    BLIDGE_OT_Sync,
    BLIDGE_OT_install_dependencies,
    BLIDGE_OT_FCurveMapperCreate,
    BLIDGE_OT_FCurveSetAnimationID,
    BLIDGE_OT_FCurveMapperClear,
    BLIDGE_OT_FCurveMapperAdd,
    BLIDGE_OT_FCurveMapperRemove,
    BLIDGE_OT_FCurveMapperChange,
    BLIDGE_OT_AddCustomProperty,
    BLIDGE_OT_RemoveCustomProperty,
    BLIDGE_OT_ObjectUniformCreate,
    BLIDGE_OT_ObjectUniformRemove,
    BLIDGE_OT_ObjectAnimationCreate,
    BLIDGE_OT_ObjectAnimationRemove,
    BLIDGE_OT_ObjectAnimationToggleUniform,
    BLIDGE_OT_AddFCurveToAnimation,
    BLIDGE_PT_Controls,
    BLIDGE_PT_install_dependencies,
    BLIDGE_PT_ObjectPropertie,
    BLIDGE_PT_FCurveMapper,
]

virtualmesh_renderer = BLidgeVirtualMeshRenderer()

def register():
    BLidgeProperties.register()

    for c in classes:
        bpy.utils.register_class(c)

    # マイグレーション: fcurve_list -> fcurve_mappings
    # 既存の.blendファイルとの互換性を保つため
    def migrate_fcurve_list():
        for scene in bpy.data.scenes:
            # 古いプロパティが存在するか確認
            if hasattr(scene.blidge, 'get') and 'fcurve_list' in scene.blidge.keys():
                # 新しいプロパティにデータをコピー
                old_list = scene.blidge['fcurve_list']
                for old_item in old_list:
                    new_item = scene.blidge.fcurve_mappings.add()
                    if 'id' in old_item:
                        new_item.id = old_item['id']
                    if 'animation_id' in old_item:
                        new_item.animation_id = old_item['animation_id']
                    if 'axis' in old_item:
                        new_item.axis = old_item['axis']
                # 古いプロパティを削除
                del scene.blidge['fcurve_list']
                print(f"BLidge: マイグレーション完了 - scene '{scene.name}' の fcurve_list を fcurve_mappings に移行しました")

    # マイグレーションを実行
    migrate_fcurve_list()

    # renderer
    virtualmesh_renderer.start(bpy.context)

    # event
    register_event()

def unregister():
    BLidgeProperties.unregister()
    
    for c in classes:
        bpy.utils.unregister_class(c)

    # renderer
    virtualmesh_renderer.end(bpy.context)

    #event
    unregister_event()

