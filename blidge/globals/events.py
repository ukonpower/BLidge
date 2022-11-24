import bpy;
from bpy.app.handlers import persistent

from .managers.fcurve import FCurveManager
from .operators.export import BLIDGE_OT_ExportGLTF

@persistent
def on_load(scene = None, context = None):
	FCurveManager.update()

@persistent
def on_save(scene = None, context = None):
	print('OT_Export')
	BLIDGE_OT_ExportGLTF.on_save()

@persistent
def on_depsgraph_update(scene = None, context = None):
	FCurveManager.update()

def register():
	bpy.app.handlers.load_post.append(on_load)
	bpy.app.handlers.save_post.append(on_save)
	bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

def unregister():
	try:
		bpy.app.handlers.load_post.remove(on_load)
		bpy.app.handlers.save_post.remove(on_save)
		bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
	except ValueError:
		pass
