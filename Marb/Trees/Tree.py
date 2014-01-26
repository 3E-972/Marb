from PySide.QtGui import QPen, QStyledItemDelegate, QBrush, QFont, QPolygon, \
QLineEdit, QRegion, QColor, QPainter, QStyleOptionViewItem
from PySide.QtCore import QSize, QRect, QPoint, QPointF, Qt, QModelIndex

from ..MarbItemDelegate import MarbItemDelegate
from ..MarbAbstractItemView import MarbAbstractItemView
from ..Global import Color

class Tree(MarbAbstractItemView):					
		def __init__(self, parent=None):
			''' Constructor. Cosntructs an instance with the given 'parent'.
			'''
			super(Tree, self).__init__( parent )
			self._realSize = QSize( 200, 200)
			self._rect = QRect( -40, -20, 80, 40 );
			self._yDistance = 50
			self._xDistance = 20
			self._depth = 0
			self._left = 0
			self._treeWidth = 0
			self._connectionPen = QPen( QColor(Color.LightGray), 2 )
			self.itemOffset = QPoint(0, 0)
			delegate = MarbItemDelegate( self )
			self.setItemDelegate( delegate )
			self._itemPos = {}
			self._itemTreePos = {}	


		def setSpacing(self, horizontal, vertical ):
			''' Sets the 'horizontal' and 'vertical' spacing between items.
			The viewport will be updated with the new spacing.
			*horizontal: integer
			*vertical: integer
			'''
			self._xDistance = horizontal
			self._yDistance = vertical
			self._positionsInView()
			self.update()
				
						
		def setConnectionPen(self, pen ):
			'''Defines the QPen used to draw the connections between items.
			*pen: QPen
			'''
			self._connectionPen = pen
		
		
		def connectionPen(self):
			'''Returns the QPen used to draw the connections between items.
			'''
			return self._connectionPen
		
		
		def scan(self, index, left, depth):
			'''Scans the tree to define the depth and width of the tree.
			[index] indicates the root which will be used to scan sub-trees
			[left]: number of feals at the left of [index]
			[depth]: depth of [index]
			*index: QModelIndex
			*left: float
			*depth: float
			'''
			raise( "Must be implemented. Should resolve the _left and _depth for each node." )
		
		
		def _positionsInTree(self):
			''' Defines the position of each item in the tree (relative position).
			'''
			raise( "Must be implemented. Should resolve the position (x,y) in the tree for each node." )


		def _positionsInView(self):
			''' Defines the position of each item in the viewport according to the 'positionsInTree()' results.
			'''
			raise( "Must be implemented. Should resolve the position (x, y) in pixel in viewport for each node." )


		def updateValues(self):
			''' Upadtes item positions.
			'''
			self._positionsInTree()
				

		def itemRect(self, index):
			''' Returns the bounding rect of the the given [index]. The bounding rect corresponds to the rectangle in which the item will be painted.
			*index: QModelIndex
			'''
			if not index.isValid():
				return QRect()
			p = QPoint(0,0)
			if index in self._itemPos:
				p	= self._itemPos[ index ] - QPointF( self.horizontalOffset(), self.verticalOffset() ) + self.itemOffset
			return self._rect.translated( p.x(), p.y() )

		
		def setItemSize(self, size ):
			''' Sets the item size to 'size'.
			*size: QSize
			'''
			self._rect = QRect( -size.width()/2, -size.height()/2, size.width(), size.height() )
#				self._rect = r
			self._positionsInView()
			self.viewport().update()
		
								
		def setX(self, index, x):
			''' Sets the X coordinates to the given [index].
			*index: QModelIndex
			*x: float
			'''
			if not index in self._itemTreePos:
					self._itemTreePos[ index ] = QPointF()
			self._itemTreePos[index].setX(x)
		
		
		def setY(self, index, y):
			''' Sets the Y coordinates to the given [index].
			*index: QModelIndex
			*y: float
			'''
			if not index in self._itemTreePos:
					self._itemTreePos[ index ] = QPointF()
					
			self._itemTreePos[index].setY(y)
				
				
		def paintEvent(self, event):
			painter = QPainter( self.viewport() )
			painter.setClipRect( event.rect() )
			painter.setRenderHint( QPainter.Antialiasing )
			self.paintConnections( painter, QPointF(0,0) )
			self.paintItems( painter )
			 
				
		def paintItems( self, painter, offset = QPointF(0,0) ):
			''' Paints the items according to positions defined by [positionInView()].
			*painter: QPainter
			*offset: QPointF
			'''
			for index in self._itemPos.keys():
				option = QStyleOptionViewItem()
				option.rect = self.itemRect( index ).translated( offset.x(), offset.y() )
				self.itemDelegate().paint( painter, option, index )
		
		
		def paintConnections( self, painter, offset = QPointF(0,0) ):
			'''Paints the connections between items.
			*painter: QPainter
			*offset: QPointF
			'''
			painter.save()
			painter.setPen( self._connectionPen )
			for index in self._itemPos.keys():
				self.paintConnectionsFor( painter, index, offset )
			painter.restore()
		
		
		def paintConnectionsFor( self, painter, index, offset ):
			''' Paints connections between an item pointed by [index] and its children.
			[offset] parametrer can be used if the view needs to offset the render (used to save as PNG file).
			*painter: QPainter
			*index: QModelIndex
			*offset: QPointF
			'''
			painter.save()
			parent = self.model().parent( index )
			if parent.isValid():
				p1 = self.itemRect(index).translated( offset.x(), offset.y() ).center()
				p2 = self.itemRect(parent).translated( offset.x(), offset.y() ).center()
				painter.drawLine( p1, p2 )
			painter.restore()

