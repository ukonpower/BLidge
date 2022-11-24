import bpy;
import re;

class FCurveManager:
	@classmethod
	def getFCurveId(cls, fcurve: bpy.types.FCurve, axis: bool = False):
		result = fcurve.data_path

		actionName = re.search(r'(?<=\(\").*?(?=\"\))', str(fcurve.id_data))
		if actionName:
			result = actionName.group() + '_' + result
		else:
			result = "unknown" + "_" + result

		if axis:
			result += '_' + 'xyzw'[fcurve.array_index]
			
		return  result
	
	@classmethod
	def update(cls):

		actionList: list[bpy.types.Action] = bpy.data.actions
		for action in actionList:
			
			curveList: list[bpy.types.FCurve] = action.fcurves
			for fcurve in curveList:
				
				exist = False
				curveId = cls.getFCurveId(fcurve, True)

				for curveData in bpy.context.scene.blidge.fcurve_list:
					if( curveData.name == curveId ):
						exist = True
						break

				if( not exist ):
					item = bpy.context.scene.blidge.fcurve_list.add()
					item.name = curveId
					item.accessor = cls.getFCurveId(fcurve)
					item.axis = 'xyzw'[fcurve.array_index]