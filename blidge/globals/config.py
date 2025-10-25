import os
import bpy


class Globals:
    """アドオンのグローバル設定"""
    path = bpy.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    libpath = bpy.path.abspath(os.path.join(os.path.dirname(path), "lib/"))
