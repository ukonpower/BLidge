import math
import bpy

from .fcurve_manager import get_fcurve_id
from ..utils.base64 import (float_array_to_base64, int_array_to_base64)

class SceneParser:

    animation_data = []

    # Parse Keyframe ----------------------

    def parse_vector(self, vector):

        parsed_vector = {}
        
        if hasattr( vector,"x" ):
            parsed_vector['x'] = vector.x
        if hasattr( vector,"y" ):
            parsed_vector['y'] = vector.y
        if hasattr( vector,"z" ):
            parsed_vector['z'] = vector.z
        if hasattr( vector,"w" ):
            parsed_vector['w'] = vector.w
            
        return parsed_vector

    def parse_keyframe(self, keyframe: bpy.types.Keyframe, beforeKeyframe: bpy.types.Keyframe):

        c = self.parse_vector(keyframe.co)

        interpolation = keyframe.interpolation[0]

        parsed_keyframe = [
            interpolation,
            [ c["x"], c["y"] ],
        ]

        if interpolation == 'B' or (beforeKeyframe != None and beforeKeyframe.interpolation[0] == 'B'):
            h_l = self.parse_vector(keyframe.handle_left)
            parsed_keyframe[1].extend([
                h_l["x"], h_l["y"] 
            ])

        if interpolation == 'B':
            h_r = self.parse_vector(keyframe.handle_right)
            parsed_keyframe[1].extend([
                h_r["x"], h_r["y"] 
            ])

        return parsed_keyframe

    def parse_keyframe_list(self, keyframes: list[bpy.types.Keyframe], invert: bool ):
        parsed_keyframes = []
        
        for i, keyframe in enumerate(keyframes):
            
            if i > 0:
                prev_keyframe = keyframes[i-1]
                parsed_keyframe = self.parse_keyframe(keyframe, prev_keyframe)
            else:
                parsed_keyframe = self.parse_keyframe(keyframe, None)

            if invert:
                parsed_keyframe[1][1] *= -1

                if( len(parsed_keyframe[1]) > 2 ):
                    parsed_keyframe[1][3] *= -1

                if( len(parsed_keyframe[1]) > 4 ):
                    parsed_keyframe[1][5] *= -1

            parsed_keyframes.append(parsed_keyframe)  
                
        return parsed_keyframes

    # Parse F-Curve ----------------------

    def parse_fcurve(self, fcurve: bpy.types.FCurve ):

        parsed_fcurve = {
            "axis": "x",
            "k": None
        }

        fcurveId = get_fcurve_id(fcurve, True)

        invert = fcurveId.find( 'location_y' ) > -1 or fcurveId.find( 'rotation_euler_y' ) > -1
        parsed_fcurve['k'] = self.parse_keyframe_list(fcurve.keyframe_points, invert)

        for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
            if( fcurve_prop.id == fcurveId):
                parsed_fcurve['axis'] = fcurve_prop.axis
                break
                
        return parsed_fcurve
    
    #  SceneGraph ----------------------

    def get_object_graph(self, object, parentName):

        type = object.blidge.type

        if object.type == 'CAMERA':
            type = 'camera'
        elif object.type == 'LIGHT':
            type = 'light'

        object_data = {
            'name': object.name,
            'class': object.blidge.blidgeClass,
            'type': type,
            'parent': parentName,
            'position': [
                object.location.x,
                object.location.z,
                -object.location.y
            ],
            'rotation': [
                object.rotation_euler.x,
                object.rotation_euler.z,
                -object.rotation_euler.y
            ],
            'scale': [
                object.scale.x,
                object.scale.z,
                object.scale.y
            ],
            'visible': not object.hide_render,
            'param': {},
        }

        # animation

        animation_list = object.blidge.animation_list
        if len(animation_list) > 0:
            object_data['animation'] = {}

            for animation in animation_list:
                print( self.animation_data["dict"] )
                if( animation.accessor in self.animation_data["dict"] ):
                    object_data['animation'][animation.name] = self.animation_data["dict"][animation.accessor]


        # children

        if len(object.children) > 0:
            object_data['children'] = []
            for child in object.children:
                object_data['children'].append(self.get_object_graph(child, object.name))

        # camera

        if object.name in bpy.data.cameras:
            camera = bpy.data.cameras[object.name]
            render = bpy.context.scene.render
            width = render.pixel_aspect_x * render.resolution_x
            height = render.pixel_aspect_y * render.resolution_y
            aspect_ratio = width / height
            fov_radian = 1.0

            if aspect_ratio >= 1.0:
                if camera.sensor_fit != 'VERTICAL':
                    fov_radian = 2.0 * math.atan(math.tan(camera.angle * 0.5) / aspect_ratio)
                else:
                    fov_radian = camera.angle
            else:
                if camera.sensor_fit != 'HORIZONTAL':
                    fov_radian = camera.angle
                else:
                    fov_radian = 2.0 * math.atan(math.tan(camera.angle * 0.5) / aspect_ratio)
                
            object_data['param'].update( {
                "fov": fov_radian / math.pi * 180
            } )

        # geometry

        if object.blidge.type == 'cube':
            object_data['param'].update( {
                "x": object.blidge.param_cube.x,
                "y": object.blidge.param_cube.z,
                "z": object.blidge.param_cube.y,
            } )

        if object.blidge.type == 'sphere':
            object_data['param'].update( {
                "r": object.blidge.param_sphere.radius,
            } )
        
        if object.blidge.type == 'plane':
            object_data['param'].update( {
                "x": object.blidge.param_plane.x,
                "y": object.blidge.param_plane.z
            } )

        # mesh

        if  object.blidge.type == 'mesh' and object.type == 'MESH':
            position = []
            normal = []
            index = []
            uv = []

            if( len( object.data.uv_layers ) > 0 ):
                for uvdata in object.data.uv_layers[0].data:
                    uv.extend([
                        uvdata.uv.x,
                        uvdata.uv.y,
                    ])

            for pl in object.data.polygons:

                for vt_index in pl.vertices:
                    vt = object.data.vertices[vt_index]

                    position.extend([
                        vt.co[0],
                        vt.co[2],
                        - vt.co[1],
                    ])

                    if( pl.use_smooth ):
                        normal.extend([
                            vt.normal[0],
                            vt.normal[2],
                            -vt.normal[1],
                        ])
                    else:
                        normal.extend([
                            pl.normal[0],
                            pl.normal[2],
                            -pl.normal[1],
                        ])
                
                lp = pl.loop_indices

                if( len( lp ) == 3 ):
                    index.extend([
                        lp[0], lp[1], lp[2]
                    ])

                if( len( lp ) == 4 ):
                    index.extend([
                        lp[0], lp[1], lp[2],
                        lp[0], lp[2], lp[3],
                    ])

            print( float_array_to_base64(position) )

            object_data['param'].update( {
                "position": float_array_to_base64(position),
                "normal": float_array_to_base64(normal),
                "uv": float_array_to_base64(uv),
                "index": int_array_to_base64(index),
            } )

        # light

        if object.type == 'LIGHT':

            light = object.data

            object_data['param']['shadowMap'] = object.blidge.param_light.shadowMap

            object_data['param']['color'] = {
                "x": light.color[0],
                "y": light.color[1],
                "z": light.color[2],
            }

            object_data['param']['intensity'] = light.energy
            
            if( light.type == 'SUN' ):
                object_data['param']['type'] = "directional"
            elif( light.type == 'SPOT'):
                object_data['param']['type'] = "spot"
                object_data['param']['intensity'] /= 500
                object_data['param'].update({
                    "angle": light.spot_size,
                    "blend": light.spot_blend
                })
            
        # material

        material = object.blidge.material

        if material.name != '' or len( material.uniform_list ) > 0:
            object_data['material'] = {}

        if material.name != '':
            object_data['material']['name'] = material.name

        if len( material.uniform_list ) > 0:
            object_data['material']['uniforms'] = {}

        for uni in material.uniform_list:
            if( uni.accessor in self.animation_data["dict"] ):
                object_data['material']['uniforms'][uni.name] = self.animation_data["dict"][uni.accessor]

        return object_data


    def get_scene_graph(self):
        objects = bpy.data.objects

        parsed_objects = {
            "name": "root",
            "parent": None,
            "children": [],
            "type": 'empty',
            "visible": True,
        }

        for object in objects:
            if( object.parent == None ):
                parsed_objects['children'].append(self.get_object_graph(object, 'root'))

        return parsed_objects

    #  Action List ----------------------

    def get_animation_list(self):
        
        animation_list = []

        # dict

        animation_dict = {}
        dict_counter = 0

        def get_fcurve_prop( fcurve ):

            fcurveAxisId = get_fcurve_id(fcurve, True)

            for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
                if( fcurve_prop.id == fcurveAxisId):
                    return fcurve_prop

            return None
        
        for action in bpy.data.actions:
        
            for fcurve in action.fcurves:
                
                fcurveProp = get_fcurve_prop( fcurve )

                if( fcurveProp != None ):
                    accessorId = fcurveProp.accessor

                    if( not( accessorId in animation_dict ) ):
                        animation_dict[accessorId] = dict_counter
                        animation_list.append([])
                        dict_counter += 1

                    animation_list[animation_dict[accessorId]].append(self.parse_fcurve(fcurve))
                    
        return { "list": animation_list, "dict": animation_dict }
    
    #  API ----------------------

    def get_scene(self):

        self.animation_data = self.get_animation_list()
        scene_graph = self.get_scene_graph()

        scene_data = {
            "animations": self.animation_data["list"],
            "root": scene_graph,
            "frame": {
                'start': bpy.context.scene.frame_start,
                'end': bpy.context.scene.frame_end,
                'fps': bpy.context.scene.render.fps,
                'playing': False
            }
        }
        return scene_data
