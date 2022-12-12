import bpy
from bpy.types import (Operator)

class BLIDGE_PT_ObjectPropertie(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        layout.prop( context.object.blidge, 'type', text='Type' )

        object_type = context.object.blidge.type

        if( object_type == 'cube' ):
            box = layout.box()
            box.label(text="Cube Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( context.object.blidge.param_cube, 'x' )
            column.prop( context.object.blidge.param_cube, 'y' )
            column.prop( context.object.blidge.param_cube, 'z' )

        if( object_type == 'sphere' ):
            box = layout.box()
            box.label(text="Sphere Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( context.object.blidge.param_sphere, 'radius' )

        if( object_type == 'plane' ):
            box = layout.box()
            box.label(text="Plane Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( context.object.blidge.param_plane, 'x' )
            column.prop( context.object.blidge.param_plane, 'z' )
