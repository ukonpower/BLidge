
import bpy, bgl
import gpu
from math import *
from mathutils import *
from gpu_extras.batch import batch_for_shader

from .geometries.geometry_cube import GeometryCube
from .geometries.geometry_sphere import GeometrySphere
from .geometries.geometry_plane import GeometryPlane

from .shaders.shader_virtual_mesh import (fragment_shader, vertex_shader)

class BLidgeVirtualMeshRenderer:

	handler = None
	shader = None

	geo_cube = None
	geo_sphere = None

	def __init__(self) -> None:
		self.shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
		self.geo_cube = GeometryCube()
		self.geo_sphere = GeometrySphere()
		self.geo_plane = GeometryPlane()

	def start(self, context):
		self.handler= bpy.types.SpaceView3D.draw_handler_add(self.draw, (context, ), 'WINDOW', 'POST_VIEW')

	def end(self, context):
		bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')

	def draw(self, context):

		self.shader.bind()

		gpu.state.depth_test_set('LESS_EQUAL')
		gpu.state.depth_mask_set(True)

		view_matrix = gpu.matrix.get_model_view_matrix()
		projection_matrix = gpu.matrix.get_projection_matrix()
		
		self.shader.uniform_float("projectionMatrix", projection_matrix)

		for obj in bpy.data.objects:

			model_matrix: Matrix = obj.matrix_world.copy()
			model_view_matrix: Matrix = view_matrix @ model_matrix

			self.shader.uniform_float( "modelViewMatrix", model_view_matrix )

			geo = None

			if obj.blidge.type == 'cube':
				geo = self.geo_cube
			elif obj.blidge.type == 'sphere': 
				geo = self.geo_sphere
			elif obj.blidge.type == 'plane': 
				geo = self.geo_plane

			if geo != None:
				batch = batch_for_shader(self.shader, 'TRIS', {"position": geo.position, "uv": geo.uv }, indices=geo.index)
				batch.draw(self.shader)

		gpu.state.depth_test_set('NONE')
		gpu.state.blend_set('NONE')
		