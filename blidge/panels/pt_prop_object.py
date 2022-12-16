import bpy
from bpy.types import (Operator)

class BLIDGE_PT_ObjectPropertie(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        object = context.object
        layout = self.layout

        object_type = object.blidge.type

        if object.type == 'CAMERA':
            blidge_type = 'camera'
            layout.label( text='Type: Camera' )
        elif object.type == 'LIGHT':
            blidge_type = 'light'
            layout.label( text='Type: Light' )
        else:
            layout.prop( object.blidge, 'type', text='Type' )

        if( object_type == 'cube' ):
            box = layout.box()
            box.label(text="Cube Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( object.blidge.param_cube, 'x' )
            column.prop( object.blidge.param_cube, 'y' )
            column.prop( object.blidge.param_cube, 'z' )

        if( object_type == 'sphere' ):
            box = layout.box()
            box.label(text="Sphere Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( object.blidge.param_sphere, 'radius' )

        if( object_type == 'plane' ):
            box = layout.box()
            box.label(text="Plane Geometry", icon='MESH_DATA')
            column = box.column(align=True)
            column.prop( object.blidge.param_plane, 'x' )
            column.prop( object.blidge.param_plane, 'z' )
