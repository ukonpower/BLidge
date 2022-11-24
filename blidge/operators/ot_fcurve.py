import bpy
from bpy.types import (Operator)

from ..utils.fcurve_manager import get_fcurve_id

class BLIDGE_OT_FCurveAccessorCreate(Operator):
    bl_idname = 'blidge.fcurve_accessor_create'
    bl_label="Create Accessor"
    bl_options = {'REGISTER', 'UNDO'}
    
    curve_id: bpy.props.StringProperty(name="Curve ID", default="" )
    curve_name: bpy.props.StringProperty(name="Curve Name", default="" )
    curve_axis: bpy.props.StringProperty(name="Curve Axis", default="" )
        
    def execute(self, context):
        item = bpy.context.scene.blidge.fcurve_list.add()
        item.id = self.curve_id
        item.name = self.curve_name
        item.axis = self.curve_axis
        
        return {'FINISHED'}

class BLIDGE_OT_FCurveAccessorRename(Operator):
    bl_idname = 'blidge.fcurve_asccessor_rename'
    bl_label="rename accessor"
    bl_options = {'REGISTER', 'UNDO'}
    
    accessor_name: bpy.props.StringProperty(name="accessor name", default="" )
    
    def invoke(self, context = None, event = None ):
        self.accessor_name = ''
        return bpy.context.window_manager.invoke_props_dialog(self)
        
    def execute(self, context):
        for fcurve in bpy.context.selected_editable_fcurves:
            fcurve_id = get_fcurve_id(fcurve, True)
            for curveData in bpy.context.scene.blidge.fcurve_list:
                if( curveData.name == fcurve_id ):
                    curveData.accessor = self.accessor_name

        bpy.context.area.tag_redraw()
        
        return {'FINISHED'}