import bpy;
from bpy.app.handlers import persistent

from ..operators.ot_export import BLIDGE_OT_GLTFExport
from ..utils.uuid import build_uuid_registry, ensure_unique_uuids

@persistent
def on_load(scene = None, context = None):
	"""ファイル読み込み時にUUID→as_pointerのマッピングを構築"""
	build_uuid_registry()

@persistent
def on_save(scene = None, context = None):
	"""ファイル保存時にUUID重複チェックとglTFエクスポート"""
	# UUID重複チェック
	fixed_count = ensure_unique_uuids()
	if fixed_count > 0:
		print(f"BLidge: {fixed_count}個のオブジェクトのUUIDを修正しました")

	# glTFエクスポート
	BLIDGE_OT_GLTFExport.on_save()

@persistent
def on_depsgraph_update(scene = None, context = None):
	pass

def register_event():
	bpy.app.handlers.load_post.append(on_load)
	bpy.app.handlers.save_post.append(on_save)
	bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

def unregister_event():
	try:
		bpy.app.handlers.load_post.remove(on_load)
		bpy.app.handlers.save_post.remove(on_save)
		bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
	except ValueError:
		pass
