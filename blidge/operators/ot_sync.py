import bpy;

from ..utils.scene_parser import SceneParser;
from ..utils.ws_server import WS;

class BLIDGE_OT_Sync(bpy.types.Operator):

    bl_idname = "blidge.sync"
    bl_label = "sync"
    bl_description = "sync"
    
    ws = WS()
    running = False

    # frame
    sended_frame = None

    @classmethod
    def is_running(cls):
        return cls.running
    
    @classmethod
    def register(cls):
        print('register')

    @classmethod
    def unregister(cls):
        print('unregister')
        cls.ws.stop_server()
        cls.running = False

        try:
            bpy.app.handlers.frame_change_pre.remove(cls.on_change_frame)
        except ValueError:
            pass
        
        try:
            bpy.app.handlers.save_post.remove(cls.on_save)
        except ValueError:
            pass

    @classmethod
    def get_frame(cls):
        scene = bpy.context.scene
        return {
            'start': scene.frame_start,
            'end': scene.frame_end,
            'current': scene.frame_current,
            "fps": scene.render.fps,
        }

    @classmethod
    def get_animation(cls):
        return SceneParser().get_scene()

    @classmethod
    def on_change_frame(cls, scene: bpy.types.Scene, any ):
        frame_data = cls.get_frame()
        if frame_data["current"] != cls.sended_frame:
            cls.ws.broadcast("sync/timeline", frame_data)
            cls.sended_frame = frame_data["current"]

    @classmethod
    def on_save(cls, scene: bpy.types.Scene, any ):
        animation_data = cls.get_animation()
        cls.ws.broadcast("sync/scene", animation_data)

    @classmethod
    def on_connect(cls, client):
        frame_data = cls.get_frame()
        animation_data = cls.get_animation()
        cls.ws.send(client, "sync/timeline", frame_data)
        cls.ws.send(client, "sync/scene", animation_data)
        
    def start(self):
        scene = bpy.context.scene
        cls = BLIDGE_OT_Sync
        cls.ws.start_server('localhost', scene.blidge.sync_port)
        cls.running = True
        bpy.app.handlers.frame_change_pre.append(cls.on_change_frame)
        bpy.app.handlers.save_post.append(cls.on_save)
            
    def stop(self):
        cls = BLIDGE_OT_Sync
        cls.ws.stop_server()
        cls.running = False
        
        try:
            bpy.app.handlers.frame_change_pre.remove(cls.on_change_frame)
        except ValueError:
            pass
        
        try:
            bpy.app.handlers.save_post.remove(cls.on_save)
        except ValueError:
            pass
        

    def execute(self, context: bpy.types.Context):
        cls = BLIDGE_OT_Sync
        cls.ws.on_connect = cls.on_connect

        if( cls.is_running() ):
            self.stop()
        else:
            self.start()

        return {'FINISHED'}