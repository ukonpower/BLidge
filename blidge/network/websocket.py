import logging
import threading
import json
import sys

from ..globals.config import Globals

sys.path.insert(0, Globals.libpath)

try:
    from websocket_server import WebsocketServer
except ImportError:
    print("websocket not found")


class CompactJSONEncoder(json.JSONEncoder):
    """数値精度を3桁に制御するカスタムJSONエンコーダー"""

    def iterencode(self, o, _one_shot=False):
        """数値を3桁に丸める"""
        for chunk in super().iterencode(o, _one_shot):
            yield chunk

    def encode(self, o):
        """オブジェクトをJSON文字列にエンコード"""
        if isinstance(o, float):
            # 小数点以下3桁に制限
            return format(round(o, 3), '.3f').rstrip('0').rstrip('.')
        return super().encode(o)


class WebSocketServer:

    server = None
    on_connect = None
    server_thread = None

    def __init__(self):
        pass

    # server

    def start_server_thread(self):
        try:
            self.server.run_forever()
        except Exception as e:
            print(f"WebSocket server error: {e}")

    def start_server(self, host, port):
        self.server = WebsocketServer(host=host, port=port, loglevel=logging.CRITICAL)
        self.server.set_fn_new_client(self.new_client)
        self.server_thread = threading.Thread(target=self.start_server_thread, daemon=True)
        self.server_thread.start()

    def stop_server(self):
        if self.server is not None:
            self.server.disconnect_clients_gracefully()
            self.server.shutdown_gracefully()
            self.server = None

    # client

    def new_client(self, client, server):
        if self.on_connect:
            self.on_connect(client)

    # send

    def get_str(self, type, data):
        return json.dumps({
            "type": type,
            "data": data
        }, cls=CompactJSONEncoder, separators=(',', ':'))

    def send(self, client, type, data):
        message_str = self.get_str(type, data)

        if self.server:
            self.server.send_message(client, message_str)

    def broadcast(self, type, data):
        message_str = self.get_str(type, data)

        if self.server:
            self.server.send_message_to_all(message_str)
