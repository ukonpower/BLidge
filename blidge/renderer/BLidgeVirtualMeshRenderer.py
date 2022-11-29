
import bpy, bgl
import gpu
from math import *
from mathutils import *
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d, draw_circle_2d
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_origin_3d, region_2d_to_vector_3d

class BLidgeVirtualMeshRenderer:

	def start(self):
		bpy.types.SpaceView3D.draw_handler_add(self.draw, 'WINDOW')

	def end(self, context):
		bpy.types.SpaceView3D.draw_handler_add(self.drawCameraFrustum, (context,), 'WINDOW', 'POST_VIEW')

	def draw(self):
		print( 'draw' )