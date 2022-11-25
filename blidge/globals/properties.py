import bpy

from ..utils.gltf import get_gltf_presets

class BLidgeFCurveProperty(bpy.types.PropertyGroup):
	index: bpy.props.IntProperty(default=0)
	id: bpy.props.StringProperty(default='')
	accessor: bpy.props.StringProperty(default='')
	axis: bpy.props.EnumProperty(
		name="axis",
        description="value axis",
        items=[
			( "x", "X", "" ),
			( "y", "Y", "" ),
			( "z", "Z", "" ),
			( "w", "W", "" ),
			( "scalar", "Scalar", "" )
		],
		default='scalar'
	)

class BLidgeControlsProperty(bpy.types.PropertyGroup):
    sync_port: bpy.props.IntProperty(name="port", default=3100)
    export_gltf_path: bpy.props.StringProperty(name="path", default="./", subtype='FILE_PATH' )
    export_gltf_preset_list: bpy.props.EnumProperty(
        name="preset",
        description="gltf export preset",
        items=get_gltf_presets(),
    )
    export_gltf_export_on_save: bpy.props.BoolProperty(name="export on save", default=False)
    export_scene_data_path: bpy.props.StringProperty(name="path", default="./", subtype='FILE_PATH')
    fcurve_list: bpy.props.CollectionProperty(type=BLidgeFCurveProperty, name="fcurve")

classes = [
    BLidgeFCurveProperty,
    BLidgeControlsProperty,
]


class BLidgeProperties():
    def register():
        for c in classes:
            bpy.utils.register_class(c)

        bpy.types.Scene.blidge = bpy.props.PointerProperty(type=BLidgeControlsProperty)

    def unregister():
        for c in classes:
            bpy.utils.unregister_class(c)

        del bpy.types.Scene.blidge