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

        # geometry

        if object.type == 'CAMERA':
            layout.label( text='Type: Camera' )
        elif object.type == 'LIGHT':
            layout.label( text='Type: Light' )
        else:
            layout.prop( object.blidge, 'type', text='Type' )

        if( object_type == 'cube' ):
            box_geometry = layout.box()
            box_geometry.label(text="Cube Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop( object.blidge.param_cube, 'x' )
            column.prop( object.blidge.param_cube, 'y' )
            column.prop( object.blidge.param_cube, 'z' )

        if( object_type == 'sphere' ):
            box_geometry = layout.box()
            box_geometry.label(text="Sphere Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop( object.blidge.param_sphere, 'radius' )

        if( object_type == 'plane' ):
            box_geometry = layout.box()
            box_geometry.label(text="Plane Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop( object.blidge.param_plane, 'x' )
            column.prop( object.blidge.param_plane, 'z' )

        # material

        box_material = layout.box()
        box_material.label(text="Material", icon='MATERIAL')
        box_material.prop( object.blidge.material, 'name' )

        scene = bpy.context.scene

        # box_material = layout.row()
        box_material.template_list("MY_UL_List", "The_List", object.blidge.material, "uniform_list", scene, "list_index")

        box_material.label(text="Uniforms", icon='MATERIAL')
        for uni in object.blidge.material.uniform_list:
            box_material.prop( uni, 'name' )

        box_material.label(text="Uniforms")
        
        box_material.operator( "blidge.object_uniform_create", text='Create', icon="PLUS" )
        


