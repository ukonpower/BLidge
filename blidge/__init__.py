bl_info = {
    "name" : "blidge",
    "author" : "ukonpower",
    "description" : "",
    "blender" : (3, 2, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Testing"
}

if "bpy" in locals():
    import imp
    imp.reload(BLidgeProperties)
    imp.reload(BLIDGE_OT_install_dependencies, BLIDGE_PT_install_dependencies)
    imp.reload(BLIDGE_OT_GLTFExport, BLIDGE_OT_SceneExport)
    imp.reload(BLIDGE_OT_Sync)
    imp.reload(BLIDGE_OT_FCurveAccessorCreate, BLIDGE_OT_FCurveAccessorRename, BLIDGE_OT_FCurveAccessorClear)
    imp.reload(BLIDGE_PT_Controls)
    imp.reload(BLIDGE_PT_ObjectPropertie)
    imp.reload(BLIDGE_PT_FCurveAccessor)
else:
    from .globals.properties import (BLidgeProperties)
    from .globals.preference import (BLIDGE_OT_install_dependencies, BLIDGE_PT_install_dependencies)
    from .operators.ot_export import (BLIDGE_OT_GLTFExport, BLIDGE_OT_SceneExport)
    from .operators.ot_sync import (BLIDGE_OT_Sync)
    from .operators.ot_fcurve import (BLIDGE_OT_FCurveAccessorCreate, BLIDGE_OT_FCurveAccessorRename, BLIDGE_OT_FCurveAccessorClear)
    from .panels.pt_view_controls import (BLIDGE_PT_Controls)
    from .panels.pt_prop_object import (BLIDGE_PT_ObjectPropertie)
    from .panels.pt_graph_fcurve import (BLIDGE_PT_FCurveAccessor)
    from .renderer.renderer_virtual_mesh import (BLidgeVirtualMeshRenderer)

import bpy

classes = [
    BLIDGE_OT_GLTFExport,
    BLIDGE_OT_SceneExport,
    BLIDGE_OT_Sync,
    BLIDGE_OT_install_dependencies,
    BLIDGE_OT_FCurveAccessorCreate,
    BLIDGE_OT_FCurveAccessorRename,
    BLIDGE_OT_FCurveAccessorClear,
    BLIDGE_PT_Controls,
    BLIDGE_PT_install_dependencies,
    BLIDGE_PT_ObjectPropertie,
    BLIDGE_PT_FCurveAccessor,
]

virtualmesh_renderer = BLidgeVirtualMeshRenderer()

def register():
    BLidgeProperties.register()

    for c in classes:
        bpy.utils.register_class(c)

    # renderer
    virtualmesh_renderer.start(bpy.context)

def unregister():
    BLidgeProperties.unregister()
    
    for c in classes:
        bpy.utils.unregister_class(c)

    # renderer
    virtualmesh_renderer.end(bpy.context)