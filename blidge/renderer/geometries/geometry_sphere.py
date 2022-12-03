import math
import mathutils

class GeometrySphere:

	position = []
	normal = []
	uv = []
	index = []

	def __init__(self, radius = 0.5, widthSegments = 30, heightSegments = 20 ):

		for i in range( heightSegments + 1 ):

			thetaI = i / heightSegments * math.pi

			segments = widthSegments if ( i != 0 and i != heightSegments ) else widthSegments

			for j in range( segments ):

				thetaJ = j / segments * math.pi * 2.0
				widthRadius = math.sin( thetaI ) * radius

				x = math.cos( thetaJ ) * widthRadius
				y = math.sin( thetaJ ) * widthRadius
				z = - math.cos( thetaI ) * radius

				self.position.append([ x, y, z ])

				self.uv.append([
					j / segments,
					i / heightSegments,
				])

				normal = mathutils.Vector([ x, y, z ])
				normal.normalize()
				self.normal.append([ normal.x, normal.y, normal.z ])

				self.index.extend([
					[
						i * widthSegments + j,
						( i + 1 ) * widthSegments + ( j + 1 ) % widthSegments,
						i * widthSegments + ( j + 1 ) % widthSegments,
					],
					[
						i * widthSegments + j,
						( i + 1 ) * widthSegments + j,
						( i + 1 ) * widthSegments + ( j + 1 ) % widthSegments,
					]
				])
