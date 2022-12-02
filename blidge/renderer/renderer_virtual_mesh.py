
import bpy, bgl
import gpu
from math import *
from mathutils import *
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d, draw_circle_2d
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_origin_3d, region_2d_to_vector_3d

class BLidgeVirtualMeshRenderer:

	handler = None

	def start(self, context):
		self.handler= bpy.types.SpaceView3D.draw_handler_add(self.draw, (context, ), 'WINDOW', 'POST_PIXEL')

	def end(self, context):
		bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')

	def draw(self, context):
		print( 'draw' )

		coords = [
			[ -1.0, 0.0, 0.0 ],
			[ 1.0, 0.0, 0.0 ],
			[ 0.0, 0.0, 1.0 ],
		]

		indices = [
			[0, 1, 2]
		]

		shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
		batch_faces = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=indices)

		shader.bind()
		shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))

		viewMatrix = gpu.matrix.get_model_view_matrix()
		projectionMatrix = gpu.matrix.get_projection_matrix()

		for obj in bpy.data.objects:

			view_matrix = obj.matrix_world.copy()

			print( viewMatrix)
			
			gpu.matrix.reset()
			gpu.matrix.load_matrix(viewMatrix @ view_matrix)
			gpu.matrix.load_projection_matrix(projectionMatrix)

			gpu.state.depth_test_set('LESS_EQUAL')
			gpu.state.depth_mask_set(True)

			batch_faces.draw(shader)

		gpu.state.depth_test_set('NONE')
		gpu.state.blend_set('NONE')
		gpu.matrix.reset()
		gpu.matrix.load_matrix(viewMatrix)
		gpu.matrix.load_projection_matrix(projectionMatrix)		
		