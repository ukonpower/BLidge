import bpy

from ..parsers import SceneParser
from ..network.websocket import WebSocketServer

class BLIDGE_OT_Sync(bpy.types.Operator):

    bl_idname = "blidge.sync"
    bl_label = "sync"
    bl_description = "sync"

    ws = WebSocketServer()
    running = False

    # frame
    sent_frame = None
    sent_playing = None
    sent_scrubbing = None

    # selection
    sent_selection = None

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
            bpy.app.handlers.frame_change_post.remove(cls.on_change_frame)
        except ValueError:
            pass

        try:
            bpy.app.handlers.save_post.remove(cls.on_save)
        except ValueError:
            pass

        try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.on_selection_change)
        except ValueError:
            pass

    @classmethod
    def get_frame(cls):
        scene = bpy.context.scene
        screen = bpy.context.screen

        playing = False
        scrubbing = False

        if screen != None:
            playing = screen.is_animation_playing
            # Blender 2.80以降で利用可能なis_scrubbingをチェック
            if hasattr(screen, 'is_scrubbing'):
                scrubbing = screen.is_scrubbing

        return {
            'start': scene.frame_start,
            'end': scene.frame_end,
            'current': scene.frame_current,
            "fps": scene.render.fps,
            'playing': playing,
            'scrubbing': scrubbing
        }

    @classmethod
    def get_animation(cls):
        return SceneParser().parse_scene()

    @classmethod
    def get_selection(cls):
        """現在の選択状態を取得"""
        try:
            # view_layerから直接アクティブオブジェクトを取得
            view_layer = bpy.context.view_layer
            active_obj = view_layer.objects.active if view_layer else None

            # 選択オブジェクトを取得
            selected_objs = []
            for obj in bpy.context.scene.objects:
                if obj.select_get():
                    selected_objs.append(obj)

            # アクティブオブジェクト
            active_data = None
            if active_obj:
                active_data = {
                    "uuid": active_obj.blidge.uuid if active_obj.blidge.uuid else "",
                    "name": active_obj.name
                }

            # 選択オブジェクトリスト
            selected_data = []
            for obj in selected_objs:
                selected_data.append({
                    "uuid": obj.blidge.uuid if obj.blidge.uuid else "",
                    "name": obj.name,
                    "type": obj.blidge.type
                })

            return {
                "active": active_data,
                "selected": selected_data
            }
        except Exception as e:
            print(f"BLidge: get_selection error: {e}")
            return {
                "active": None,
                "selected": []
            }

    @classmethod
    def on_change_frame(cls, scene: bpy.types.Scene, any):
        frame_data = cls.get_frame()
        if (frame_data["current"] != cls.sent_frame or
            frame_data["playing"] != cls.sent_playing or
            frame_data["scrubbing"] != cls.sent_scrubbing):
            cls.ws.broadcast("sync/timeline", frame_data)
            cls.sent_frame = frame_data["current"]
            cls.sent_playing = frame_data["playing"]
            cls.sent_scrubbing = frame_data["scrubbing"]
    
    @classmethod
    def on_start_playing(cls, scene: bpy.types.Scene, any):
        frame_data = cls.get_frame()
        frame_data["playing"] = True
        cls.ws.broadcast("sync/timeline", frame_data)

    @classmethod
    def on_stop_playing(cls, scene: bpy.types.Scene, any):
        frame_data = cls.get_frame()
        frame_data["playing"] = False
        cls.ws.broadcast("sync/timeline", frame_data)

    @classmethod
    def on_save(cls, scene: bpy.types.Scene, any):
        animation_data = cls.get_animation()
        cls.ws.broadcast("sync/scene", animation_data)

    @classmethod
    def on_selection_change(cls, scene, depsgraph):
        """選択状態の変更を検出して通知"""
        selection_data = cls.get_selection()

        # 前回と同じ選択状態なら送信しない(最適化)
        if selection_data != cls.sent_selection:
            cls.ws.broadcast("sync/selection", selection_data)
            cls.sent_selection = selection_data

    @classmethod
    def on_connect(cls, client):
        frame_data = cls.get_frame()
        animation_data = cls.get_animation()
        selection_data = cls.get_selection()
        cls.ws.send(client, "sync/timeline", frame_data)
        cls.ws.send(client, "sync/scene", animation_data)
        cls.ws.send(client, "sync/selection", selection_data)
        
    def start(self):
        scene = bpy.context.scene
        cls = BLIDGE_OT_Sync
        cls.ws.start_server(scene.blidge.sync_host, scene.blidge.sync_port)
        cls.running = True
        bpy.app.handlers.frame_change_post.append(cls.on_change_frame)
        bpy.app.handlers.animation_playback_pre.append(cls.on_start_playing)
        bpy.app.handlers.animation_playback_post.append(cls.on_stop_playing)
        bpy.app.handlers.save_post.append(cls.on_save)
        bpy.app.handlers.depsgraph_update_post.append(cls.on_selection_change)
            
    def stop(self):
        cls = BLIDGE_OT_Sync
        cls.ws.stop_server()
        cls.running = False

        try:
            bpy.app.handlers.frame_change_post.remove(cls.on_change_frame)
            bpy.app.handlers.animation_playback_pre.remove(cls.on_start_playing)
            bpy.app.handlers.animation_playback_post.remove(cls.on_stop_playing)
        except ValueError:
            pass

        try:
            bpy.app.handlers.save_post.remove(cls.on_save)
        except ValueError:
            pass

        try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.on_selection_change)
        except ValueError:
            pass
        

    def execute(self, context: bpy.types.Context):
        cls = BLIDGE_OT_Sync
        cls.ws.on_connect = cls.on_connect

        if cls.is_running():
            self.stop()
        else:
            self.start()

        return {'FINISHED'}