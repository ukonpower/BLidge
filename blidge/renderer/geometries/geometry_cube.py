class GeometryCube:

	position = None
	normal = None
	index = None
	uv = None

	def __init__(self, x, y, z):

		hx = x / 2
		hy = y / 2
		hz = z / 2

		self.position = [
			
			[ - hx, - hy, hz ],
			[ hx, - hy, hz ],
			[ hx, hy, hz ],
			[ - hx, hy, hz ],
			
			[ - hx, hy, - hz ],
			[ hx, hy, - hz ],
			[ hx, - hy, - hz ],
			[ - hx, - hy, - hz ],

			[ hx, - hy, - hz ],
			[ hx, hy, - hz ],
			[ hx, hy, hz ],
			[ hx, - hy, hz ],

			[ - hx, hy, - hz ],
			[ - hx, - hy, - hz ],
			[ - hx, - hy, hz ],
			[ - hx, hy, hz ],

			[ -hx, - hy, - hz ],
			[ hx, - hy, - hz ],
			[ hx, - hy, hz ],
			[ - hx, - hy, hz ],

			[ hx, hy, - hz ],
			[ - hx, hy, - hz ],
			[ -hx, hy, hz ],
			[ hx, hy, hz ]
		]

		self.normal = [
			[ 0, 0, 1 ],
			[ 0, 0, 1 ],
			[ 0, 0, 1 ],
			[ 0, 0, 1 ],
			[ 0, 0, - 1 ],
			[ 0, 0, - 1 ],
			[ 0, 0, - 1 ],
			[ 0, 0, - 1 ],
			[ 1, 0, 0 ],
			[ 1, 0, 0 ],
			[ 1, 0, 0 ],
			[ 1, 0, 0 ],
			[ - 1, 0, 0 ],
			[ - 1, 0, 0 ],
			[ - 1, 0, 0 ],
			[ - 1, 0, 0 ],
			[ 0, 1, 0 ],
			[ 0, 1, 0 ],
			[ 0, 1, 0 ],
			[ 0, 1, 0 ],
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
			[ 0, - 1, 0 ],
		]

		self.index = []
		self.uv = []

		for i in range( 6 ):

			offset = 4 * i

			self.index.extend([
				[ 0 + offset, 1 + offset, 2 + offset ],
				[ 0 + offset, 2 + offset, 3 + offset ]
			])

			self.uv.extend([
				[ 0, 0 ],
				[ 1, 0 ],
				[ 1, 1 ],
				[ 0, 1 ],
			])
