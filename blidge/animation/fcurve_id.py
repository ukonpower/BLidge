import bpy;
import re;

def get_fcurve_id(fcurve: bpy.types.FCurve, axis: bool = False):
	result = ""

	actionName = re.search(r'(?<=\(\").*?(?=\"\))', str(fcurve.id_data))
	if actionName:
		result = actionName.group() + '_' + fcurve.data_path
	else:
		result = "unknown" + "_" + fcurve.data_path

	if axis:
		result += '_' + 'xyzw'[fcurve.array_index]

	return  result

def get_fcurve_prop( id: str ):
	for fcurve_property in bpy.context.scene.blidge.fcurve_mappings:
		if fcurve_property.id == id:
			return fcurve_property

	return None

def get_action_fcurves(action: bpy.types.Action):
	"""Action に含まれる全 F-Curve を返す"""
	# Blender 5.0 で Action.fcurves が削除され、F-Curve は layers → strips → channelbags の下に置かれる
	fcurves = []

	for layer in action.layers:
		for strip in layer.strips:
			for channelbag in strip.channelbags:
				for fcurve in channelbag.fcurves:
					fcurves.append(fcurve)

	return fcurves

def get_object_channelbag(obj: bpy.types.Object):
	"""オブジェクトに割り当てられた Action スロットの channelbag を返す。無ければ None"""
	from bpy_extras import anim_utils

	animation_data = obj.animation_data

	if not animation_data or not animation_data.action or not animation_data.action_slot:
		return None

	return anim_utils.action_get_channelbag_for_slot(animation_data.action, animation_data.action_slot)
