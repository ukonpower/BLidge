class GeometryPlane:

	position = None
	normal = None
	index = None
	uv = None

	def __init__(self, x = 1, y = 1):

		hx = x / 2
		hy = y / 2

		self.position = [
			[ -hx, 0, - hy ],
			[ hx, 0, - hy ],
			[ hx, 0, hy ],
			[ -hx, 0, hy ]
		]

		self.normal = [
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
		]
		
		self.index = [
			[ 0, 1, 2 ],
			[ 0, 2, 3 ]
		]

		self.uv = [
			[ 0, 0 ],
			[ 1, 0 ],
			[ 1, 1 ],
			[ 0, 1 ],
		]

