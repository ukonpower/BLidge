import bpy
import sys
from bpy.types import AddonPreferences
from pathlib import Path

class BLIDGE_OT_install_dependencies(bpy.types.Operator):
	bl_idname = "blidge.install_dependencies"
	bl_label = "Install Dependencies"
	bl_description = "Install dependencies"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):

		import subprocess

		py_exec = str(sys.executable)
		module = 'websockets'

		lib_path = Path(py_exec).parent.parent / "lib/site-packages"
		subprocess.call([py_exec, "-m", "ensurepip", "--user" ])
		subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip" ])
		subprocess.call([py_exec,"-m", "pip", "install", f"--target={str(lib_path)}", module])

		return {'FINISHED'}
	
class BLIDGE_PT_install_dependencies(AddonPreferences):
	bl_idname = __package__

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("blidge.install_dependencies")