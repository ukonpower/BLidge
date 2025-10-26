import bpy
import uuid

from ..utils.gltf import get_gltf_presets


def ensure_animation_id(self, context):
    """アニメーションIDが空の場合、UUIDを自動生成"""
    if not self.id:
        self.id = str(uuid.uuid4())


class BLidgeFCurveProperty(bpy.types.PropertyGroup):
	index: bpy.props.IntProperty(default=0)
	id: bpy.props.StringProperty(default='')
	animation_id: bpy.props.StringProperty(
		name="Animation ID",
		description="紐づくアニメーション項目のID",
		default=''
	)
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
    sync_host: bpy.props.StringProperty(name="host", default="localhost")
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
    object_animation_list_index: bpy.props.IntProperty(name = "object animation list index", default = 0)

class BLidgeGeometryCubeProperty(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty(default=2)
    y: bpy.props.FloatProperty(default=2)
    z: bpy.props.FloatProperty(default=2)

class BLidgeGeometryPlaneProperty(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty(default=2)
    z: bpy.props.FloatProperty(default=2)

class BLidgeGeometrySphereProperty(bpy.types.PropertyGroup):
    radius: bpy.props.FloatProperty(default=1)

class BLidgeLightProperty(bpy.types.PropertyGroup):
    shadow_map: bpy.props.BoolProperty(default=False)

class BLidgeCustomProperty(bpy.types.PropertyGroup):
    """BLidge管理下のカスタムプロパティ"""
    name: bpy.props.StringProperty(
        name="名前",
        description="カスタムプロパティの名前",
        default="custom_property"
    )

    prop_type: bpy.props.EnumProperty(
        name="型",
        items=[
            ('FLOAT', 'Float', '浮動小数点数'),
            ('INT', 'Int', '整数'),
            ('BOOL', 'Bool', 'ブール値'),
        ],
        default='FLOAT'
    )

    # 実際の値
    value_float: bpy.props.FloatProperty(name="値", default=0.0)
    value_int: bpy.props.IntProperty(name="値", default=0)
    value_bool: bpy.props.BoolProperty(name="値", default=False)

class BLidgeAnimationProperty(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty(
        name="ID",
        description="アニメーション項目の一意のID",
        default='',
        update=ensure_animation_id
    )
    name: bpy.props.StringProperty(
        name="名前",
        description="Uniformとして使用する際の変数名",
        default=''
    )
    editable: bpy.props.BoolProperty(default=True)
    as_uniform: bpy.props.BoolProperty(
        name="Uniformとして使用",
        description="このアニメーションをマテリアルのUniformとして使用する",
        default=False
    )

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
			( "light", "Light", "" ),
			( "cylinder", "Cylinder", "" ),
			( "gltf", "glTF", "" ),
		],
		default='empty',
	)
    param_cube: bpy.props.PointerProperty( type=BLidgeGeometryCubeProperty)
    param_plane: bpy.props.PointerProperty( type=BLidgeGeometryPlaneProperty)
    param_sphere: bpy.props.PointerProperty( type=BLidgeGeometrySphereProperty)
    param_light: bpy.props.PointerProperty( type=BLidgeLightProperty)
    custom_property_list: bpy.props.CollectionProperty(type=BLidgeCustomProperty)
    custom_properties_expanded: bpy.props.BoolProperty(name="Custom Properties Expanded", default=False)
    animation_list: bpy.props.CollectionProperty(type=BLidgeAnimationProperty)
    render_virtual_mesh: bpy.props.BoolProperty(default=False)

classes = [
    BLidgeGeometryCubeProperty,
    BLidgeGeometryPlaneProperty,
    BLidgeGeometrySphereProperty,
    BLidgeLightProperty,
    BLidgeFCurveProperty,
    BLidgeControlsProperty,
    BLidgeCustomProperty,
    BLidgeAnimationProperty,
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