import bpy
from bpy.types import (UIList)

def createAccesorList(self,context):
    context.scene.blidge.accessor_list.clear()
    for item in context.scene.blidge.fcurve_list:
        name = item.accessor
        if ( name in context.scene.blidge.accessor_list ) == False:
            new_item = context.scene.blidge.accessor_list.add()
            new_item.name = item.accessor

class BLidgeUniformListValues(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(default='name')

class BLIDGE_UL_Uniforms(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, 'name', text="", emboss=False, icon="CUBE")
        row.prop_search(item, 'value', context.scene.blidge, 'accessor_list', text='', icon="FCURVE")
        ot_remove = row.operator( "blidge.object_uniform_remove", text='', icon='CANCEL', emboss=False )
        ot_remove.item_index = index


    