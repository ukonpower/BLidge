from ast import Str
import bpy

from ..managers.fcurve import FCurveManager

class SceneParser:

    # Parse Keyframe ----------------------

    def parse_vector(self, vector):
        parsed_vector = {}
        if hasattr( vector,"x" ):
            parsed_vector["x"] = vector.x
        if hasattr( vector,"y" ):
            parsed_vector["y"] = vector.y
        if hasattr( vector,"z" ):
            parsed_vector["z"] = vector.z
        if hasattr( vector,"w" ):
            parsed_vector["w"] = vector.w
            
        return parsed_vector

    def get_fcurve_axis(self, fcurveId: str, axis: str):

        axisList = 'xyzw'

        if( not fcurveId.find( 'Shader NodetreeAction' ) > -1 ):
            axisList = 'xzyw'

        axisIndex = axisList.find(axis)

        return 'xyzw'[axisIndex]

    def parse_keyframe(self, keyframe: bpy.types.Keyframe):
        parsed_keyframe = {
                "c": self.parse_vector(keyframe.co),
                "h_l": self.parse_vector(keyframe.handle_left),
                "h_r": self.parse_vector(keyframe.handle_right),
                "e": keyframe.easing,
                "i": keyframe.interpolation
        }
        return parsed_keyframe

    def parse_keyframe_list(self, keyframes: list[bpy.types.Keyframe], invert: bool ):
        parsed_keyframes = []
        for keyframe in keyframes:
            parsed_keyframe = self.parse_keyframe(keyframe)

            if invert:
                parsed_keyframe["c"]["y"] *= -1
                parsed_keyframe["h_l"]["y"] *= -1
                parsed_keyframe["h_r"]["y"] *= -1

            parsed_keyframes.append(parsed_keyframe)
                
        return parsed_keyframes

    # Parse F-Curve ----------------------

    def parse_fcurve(self, fcurve: bpy.types.FCurve ):

        parsed_fcurve = {
            "name": "none",
            "axis": "scaler",
            "keyframes": None
        }

        fcurveId = FCurveManager.getFCurveId(fcurve, True)

        invert = fcurveId.find( 'location_y' ) > -1 or fcurveId.find( 'rotation_euler_y' ) > -1
        parsed_fcurve['keyframes'] = self.parse_keyframe_list(fcurve.keyframe_points, invert)

        for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
            if( fcurve_prop.name == fcurveId):
                parsed_fcurve["name"] = fcurve_prop.accessor
                parsed_fcurve["axis"] = self.get_fcurve_axis( fcurveId, fcurve_prop.axis )
                
        return parsed_fcurve
    
    # Parse Action ----------------------

    def parse_action(self, action: bpy.types.Action ):

        fcurve_accessor_list = []
        
        for fcurve in action.fcurves:
            fcurveId = FCurveManager.getFCurveId(fcurve, True)
            for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
                if( fcurve_prop.name == fcurveId and not fcurve_prop.accessor in fcurve_accessor_list):
                    fcurve_accessor_list.append(fcurve_prop.accessor)
                
        return {
            "name": action.name_full,
            "fcurves": fcurve_accessor_list
        }

    #  SceneGraph ----------------------

    def get_object_graph(self, object, parentName):

        object_data = {
            "name": object.name,
            "parent": parentName,
            "children": [],
            "position": {
                "x": object.location.x,
                "y": object.location.z,
                "z": -object.location.y
            },
            "rotation": {
                "x": object.rotation_euler.x,
                "y": object.rotation_euler.z,
                "z": -object.rotation_euler.y
            },
            "scale": {
                "x": object.scale.x,
                "y": object.scale.z,
                "z": object.scale.y
            },
            "actions": []
        }

        object_animation_data = object.animation_data
            
        if object_animation_data:
            object_data["actions"].append( object_animation_data.action.name_full )

        for matSlot in object.material_slots:
            mat_animation_data = matSlot.material.node_tree.animation_data
            # if object_animation_data:
                # object_data["actions"].append( mat_animation_data.action.name_full )

        for child in object.children:
            object_data["children"].append(self.get_object_graph(child, object.name))

        return object_data


    def get_scene_graph(self):
        objects = bpy.data.objects

        parsed_objects = {
            "name": "root",
            "children": [],
            "parent": None,
            "position": { "x": 0.0, "y": 0.0, "z": 0.0 },
            "rotation": { "x": 0.0, "y": 0.0, "z": 0.0 },
            "scale": { "x": 1.0, "y": 1.0, "z": 1.0 }
        }

        for object in objects:
            if( object.parent == None ):
                parsed_objects["children"].append(self.get_object_graph(object, 'root'))

        return parsed_objects

    #  Action List ----------------------

    def get_action_list(self):
        parsed_action_list = []

        for action in bpy.data.actions:
            parsed_action_list.append( self.parse_action(action) )
        
        return parsed_action_list

    #  Action List ----------------------

    def get_fcurve_list(self):
        parse_fcurve_list = []

        actionList: list[bpy.types.Action] = bpy.data.actions
        for action in actionList:
            
            curveList: list[bpy.types.FCurve] = action.fcurves
            for fcurve in curveList:
                parse_fcurve_list.append( self.parse_fcurve(fcurve) )
        
        return parse_fcurve_list
    
    #  API ----------------------

    def get_scene(self):
        scene_data = {
            "scene": self.get_scene_graph(),
            "actions": self.get_action_list(),
            "fcurves": self.get_fcurve_list(),
        }
        return scene_data
