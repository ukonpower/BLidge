import bpy

from ..utils.fcurve_manager import get_fcurve_id
from ..operators.ot_fcurve import (BLIDGE_OT_FCurveAccessorCreate, BLIDGE_OT_FCurveAccessorRename)

class BLIDGE_PT_FCurve(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'F-Curve'

    def draw(self, context):
        layout = self.layout

        for fcurve in bpy.context.selected_editable_fcurves:
            fcurve_id = get_fcurve_id(fcurve, axis=True)
            layout.label(text=fcurve_id)

            curve_data = None
            
            for curve in bpy.context.scene.blidge.fcurve_list:
                if( curve.id == fcurve_id ):
                    curve_data = curve
                    break
            
            if curve_data:
                layout.prop(curve_data, 'id', text='name')
                layout.prop(curve_data, 'axis', text='axis')
            else:
                layout.label(text='not found')
                op_create = layout.operator( BLIDGE_OT_FCurveAccessorCreate.bl_idname )
                op_create.curve_id = fcurve_id
                op_create.curve_name = fcurve_id
                op_create.curve_axis = 'x'
                


        layout.operator( BLIDGE_OT_FCurveAccessorRename.bl_idname, text='Rename accessors' )
