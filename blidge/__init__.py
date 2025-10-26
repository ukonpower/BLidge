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
    imp.reload(BLIDGE_OT_AddFCurveToAccessor)
    imp.reload(BLIDGE_OT_FCurveAccessorCreate)
    imp.reload(BLIDGE_OT_FCurveAccessorRename)
    imp.reload(BLIDGE_OT_FCurveAccessorClear)
    imp.reload(BLIDGE_PT_Controls)
    imp.reload(BLIDGE_PT_ObjectPropertie)
    imp.reload(BLIDGE_PT_FCurveAccessor)
    imp.reload(BLIDGE_UL_Uniforms)
    imp.reload(BLIDGE_UL_Animations)
    imp.reload(BLidgeVirtualMeshRenderer)
else:
    import bpy
    from .globals.config import Globals
    from .globals.properties import BLidgeProperties
    from .globals.preference import BLIDGE_OT_install_dependencies, BLIDGE_PT_install_dependencies
    from .operators.ot_export import BLIDGE_OT_GLTFExport, BLIDGE_OT_SceneExport
    from .operators.ot_sync import BLIDGE_OT_Sync
    from .operators.ot_fcurve import BLIDGE_OT_FCurveAccessorCreate, BLIDGE_OT_FCurveAccessorRename, BLIDGE_OT_FCurveAccessorClear
    from .operators.ot_object import BLIDGE_OT_AddCustomProperty, BLIDGE_OT_RemoveCustomProperty, BLIDGE_OT_ObjectUniformCreate, BLIDGE_OT_ObjectUniformRemove, BLIDGE_OT_ObjectAnimationCreate, BLIDGE_OT_ObjectAnimationRemove, BLIDGE_OT_ObjectAnimationToggleUniform, BLIDGE_OT_AddFCurveToAccessor
    from .panels.pt_view_controls import BLIDGE_PT_Controls
    from .panels.pt_prop_object import BLIDGE_PT_ObjectPropertie
    from .panels.pt_graph_fcurve import BLIDGE_PT_FCurveAccessor
    from .ui.ui_list import BLIDGE_UL_Uniforms, BLIDGE_UL_Animations
    from .renderer.renderer_virtual_mesh import BLidgeVirtualMeshRenderer
    from .globals.events import register_event, unregister_event

classes = [
    BLIDGE_OT_GLTFExport,
    BLIDGE_OT_SceneExport,
    BLIDGE_OT_Sync,
    BLIDGE_OT_install_dependencies,
    BLIDGE_OT_FCurveAccessorCreate,
    BLIDGE_OT_FCurveAccessorRename,
    BLIDGE_OT_FCurveAccessorClear,
    BLIDGE_OT_AddCustomProperty,
    BLIDGE_OT_RemoveCustomProperty,
    BLIDGE_OT_ObjectUniformCreate,
    BLIDGE_OT_ObjectUniformRemove,
    BLIDGE_OT_ObjectAnimationCreate,
    BLIDGE_OT_ObjectAnimationRemove,
    BLIDGE_OT_ObjectAnimationToggleUniform,
    BLIDGE_OT_AddFCurveToAccessor,
    BLIDGE_PT_Controls,
    BLIDGE_PT_install_dependencies,
    BLIDGE_PT_ObjectPropertie,
    BLIDGE_PT_FCurveAccessor,
    BLIDGE_UL_Animations,
    BLIDGE_UL_Uniforms,
]

virtualmesh_renderer = BLidgeVirtualMeshRenderer()

def register():
    BLidgeProperties.register()

    for c in classes:
        bpy.utils.register_class(c)

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

