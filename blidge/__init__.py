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
    imp.reload(BLIDGE_OT_ExportGLTF)
    imp.reload(BLIDGE_OT_ExportSceneData)
    imp.reload(BLIDGE_PT_MainControls)
else:
    from .operators.export import (BLIDGE_OT_ExportGLTF, BLIDGE_OT_ExportSceneData)
    from .panels.blidge import (BLIDGE_PT_MainControls)


import bpy

classes = [
    BLIDGE_OT_ExportGLTF,
    BLIDGE_OT_ExportSceneData,
    BLIDGE_PT_MainControls
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)