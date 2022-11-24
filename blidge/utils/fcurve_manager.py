import bpy;
import re;

def get_fcurve_id(fcurve: bpy.types.FCurve, axis: bool = False):
	result = fcurve.data_path

	actionName = re.search(r'(?<=\(\").*?(?=\"\))', str(fcurve.id_data))
	if actionName:
		result = actionName.group() + '_' + result
	else:
		result = "unknown" + "_" + result

	if axis:
		result += '_' + 'xyzw'[fcurve.array_index]
		
	return  result