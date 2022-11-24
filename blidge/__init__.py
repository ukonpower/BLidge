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
    imp.reload(BLIDGE_PT_Controls)
    imp.reload(BLIDGE_OT_ExportGLTF)
    imp.reload(BLIDGE_OT_ExportSceneData)
    imp.reload(BLIDGE_OT_Sync)
else:
    from .globals.properties import (BLidgeProperties)
    from .globals.preference import (BLIDGE_OT_install_dependencies, BLIDGE_PT_install_dependencies)
    from .operators.ot_export import (BLIDGE_OT_ExportGLTF, BLIDGE_OT_ExportSceneData)
    from .operators.ot_sync import (BLIDGE_OT_Sync)
    from .operators.ot_fcurve import (BLIDGE_OT_FCurveAccessorCreate,BLIDGE_OT_FCurveAccessorRename)
    from .panels.pt_view_controls import (BLIDGE_PT_Controls)
    from .panels.pt_prop_object import (BLIDGE_PT_ObjectPropertie)
    from .panels.pt_graph_fcurve import (BLIDGE_PT_FCurve)

import bpy

classes = [
    BLIDGE_OT_ExportGLTF,
    BLIDGE_OT_ExportSceneData,
    BLIDGE_OT_Sync,
    BLIDGE_OT_install_dependencies,
    BLIDGE_OT_FCurveAccessorCreate,
    BLIDGE_OT_FCurveAccessorRename,
    BLIDGE_PT_Controls,
    BLIDGE_PT_install_dependencies,
    BLIDGE_PT_ObjectPropertie,
    BLIDGE_PT_FCurve
]

def register():
    BLidgeProperties.register()

    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    BLidgeProperties.unregister()
    
    for c in classes:
        bpy.utils.unregister_class(c)