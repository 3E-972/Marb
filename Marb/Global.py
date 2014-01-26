from PySide.QtGui import QColor

def enum(**enums):
	return type( 'Enum', (), enums)
	

class Color:
	'''List of predefined colors
	'''
	Blue		= 0x6090e4
	Green		= 0x9AEC7A
	Purple		= 0x8600C8
	Red			= 0xDB0000
	Orange		= 0xFF8000
	Yellow      = 0xFDEF46
	Gray		= 0x868686
		
	LightBlue	= 0x2BBEEF
	LightGreen	= 0xc9ff71
	LightPurple = 0x8274B0
	LightRed	= 0xFF5656
	LightOrange = 0xFFB366
	LightYellow = 0xFFFF99
	LightGray	= 0xBEBEBE
	
	DarkBlue   = 0x0839A1
	DarkGreen  = 0x84D000
	DarkPurple = 0x7300AB
	DarkRed	   = 0xBA0000
	DarkOrange = 0xFFF219
	DarkYellow = 0xFFD320
	DarkGray   = 0x505050
	
	__regularColors = [ Blue, Green, Purple, Red, Orange, Yellow, Gray	]
	__lightColors = [ LightBlue, LightGreen, LightPurple, LightRed, LightOrange, LightYellow, LightGray	]
	__darkColors = [ DarkBlue, DarkGreen, DarkPurple, DarkRed, DarkOrange, DarkYellow, DarkGray	]
	
	@staticmethod
	def regularColorAt(index):
		''' Returns the regular (not light, not dark) color corresponding to the index.
		
		Used to set a default color
		'''
		return QColor(Color().__regularColors[index%len(Color().__regularColors)])
	

	@staticmethod
	def lightColorAt(index):
		''' Returns the light color corresponding to the index.
		
		Used to set a default color.
		'''
		i = index % len( Color().__lightColors )
		return QColor(Color().__lightColors[i])
	
	@staticmethod
	def darkColorAt(index):
		''' Returns the dark color corresponding to the index.
		
		Used to set a default color.
		'''
		i = index % len( Color().__darkColors )
		return QColor(Color().__darkColors[i])
	
	@staticmethod
	def colorAt( index ):
		t = Color().__regularColors + Color().__lightColors + Color().__darkColors
		return QColor(t[index % len(t) ])


class Shape:
	'''List of available shapes for the points
	'''
	Rectangle = 0
	Ellipse	 = 1
	RoundedRect = 2
	Diamond = 3
	Triangle = 4
	ReversedTriangle = 5


class Type:
	'''List of available types for the linear chart
	'''
	Point = 1
	Line	= 2
	Bar	 = 4

class Render:
	Plain = 1
	Translucent = 2
	Wireframe = 3


class DistancePolicy:
	IgnoreDistance = 0
	KeepDistance = 1
