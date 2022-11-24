import bpy

from ..globals.properties import BLidgeFCurveProperty
from ..operators.f_curve import BLIDGE_OT_FCurveAccessorRename

class BLIDGE_PT_FCurve(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'F-Curve'

    def draw(self, context):
        layout = self.layout
        for fcurve in bpy.context.selected_editable_fcurves:
            accessor = fcurve.blidge_accessor

            print( fcurve.blidge_accessor )
            # layout.label(text="aaa")
            # layout.prop(accessor.name, text='name')
            # layout.prop(accessor.axis, text='axis')

            # fcurve_id = FCurveManager.getFCurveId(fcurve, True)
            # for curveData in bpy.context.scene.blidge.fcurve_list:
            #     if( curveData.name == fcurve_id ):

        layout.operator( BLIDGE_OT_FCurveAccessorRename.bl_idname, text='Rename accessors' )
