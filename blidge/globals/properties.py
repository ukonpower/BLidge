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
		],
		default='x'
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

class BLidgeGeometryCubeProperty(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty(default=1)
    y: bpy.props.FloatProperty(default=1)
    z: bpy.props.FloatProperty(default=1)

class BLidgeGeometryPlaneProperty(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty(default=1)
    z: bpy.props.FloatProperty(default=1)

class BLidgeGeometrySphereProperty(bpy.types.PropertyGroup):
    radius: bpy.props.FloatProperty(default=0.5)

class BLidgeObjectProperty(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
		name="type",
        description="object type",
        items=[
			( "empty", "Empty", "" ),
			( "cube", "Cube", "" ),
			( "plane", "Plane", "" ),
			( "sphere", "Sphere", "" ),
			( "mesh", "Mesh", "" ),
			( "camera", "Camera", "" ),
		],
		default='empty'
	)
    param_cube: bpy.props.PointerProperty( type=BLidgeGeometryCubeProperty)
    param_plane: bpy.props.PointerProperty( type=BLidgeGeometryPlaneProperty)
    param_sphere: bpy.props.PointerProperty( type=BLidgeGeometrySphereProperty)

classes = [
    BLidgeGeometryCubeProperty,
    BLidgeGeometryPlaneProperty,
    BLidgeGeometrySphereProperty,
    BLidgeFCurveProperty,
    BLidgeControlsProperty,
    BLidgeObjectProperty,
]

class BLidgeProperties():
    def register():
        for c in classes:
            bpy.utils.register_class(c)

        bpy.types.Scene.blidge = bpy.props.PointerProperty(type=BLidgeControlsProperty)
        bpy.types.Object.blidge = bpy.props.PointerProperty(type=BLidgeObjectProperty)

    def unregister():
        for c in classes:
            bpy.utils.unregister_class(c)

        del bpy.types.Scene.blidge
        del bpy.types.Object.blidge