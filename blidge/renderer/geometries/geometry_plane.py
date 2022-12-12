class GeometryPlane:

	size = [ None, None ]

	position = None
	normal = None
	index = None
	uv = None

	def __init__(self, x = 1, y = 1):

		self.setSize( x, y )

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

	def setSize( self, x = 1, y = 1 ):

		if self.size[0] == x and self.size[1] == y: return
		
		self.size[0] = x
		self.size[1] = y

		hx = x / 2
		hy = y / 2

		self.position = [
			[ -hx, 0, - hy ],
			[ hx, 0, - hy ],
			[ hx, 0, hy ],
			[ -hx, 0, hy ]
		]