from ..Global import Color
from .Chart import Chart, ChartStyle
from .Axis import RadialAxis

from PySide.QtGui import QPainter, QPen, QColor, QFontMetrics, QPainterPath, QBrush
from PySide.QtCore import QSize, QRect, QPointF, QPoint, Qt

class RadialChart(Chart):
    def __init__(self, parent=None):
        ''' Constructor. Constructs an instance with the given [parent].
        *parent: QWidget
        '''
        super(RadialChart, self).__init__( parent )
        self._axis = RadialAxis()


    def columnStyle(self, column ):
        '''Returns the style for the column.
        If no style has been set for the column, returns the style by default
        *column: integer
        '''
        if column in self._style:
            return self._style[ column ]
        else:
            style = ChartStyle()
            c1 = Color.lightColorAt( column )
            c2 = Color.regularColorAt( column )
            c1.setAlpha( 200 )
            style.setPen( QPen( QColor(c2), 2 ) )
            style.setBrush( QBrush(c1) )
            return style


    def itemPath( self, index ):
        '''Returns the bounding path for the item pointed by the [index].
        *index: QModelIndex
        '''
        angle = float( self._axis.stepSize() / self.model().columnCount() )
        delta = 0.1 * angle
        startAngle = angle * index.column()
        startAngle += index.row() * self._axis.stepSize()
        pathCenter = QPainterPath()
        rectangle = QRect( -self._axis.centerHoleDiam/2, -self._axis.centerHoleDiam/2, self._axis.centerHoleDiam, self._axis.centerHoleDiam )
        rectangle.translate( self._axis._valuesRect.center() )
        pathCenter.addEllipse( rectangle )
        value = 0.0
        try:
            value = float(index.data())
        except:
            pass
        rectangle = self._axis.valueToRect( value )
        path = QPainterPath()
        path.moveTo( self._axis._valuesRect.center() )
        path.arcTo( rectangle, (startAngle + delta), (angle - delta * 2) )
        path.closeSubpath();
        path = path.subtracted( pathCenter )
        return path


# 0 0.0 32.20132469929538 322.0132469929538 -32.20132469929538 -257.610597594363

# 1 322.0132469929538 32.20132469929538 322.0132469929538 -354.21457169224914 -257.610597594363

# 2 644.0264939859076 32.20132469929538 322.0132469929538 -676.2278186852029 -257.610597594363

# 3 966.0397409788613 32.20132469929538 322.0132469929538 -998.2410656781567 -257.610597594363

    def paintChart(self, painter):  
        ''' Paints the chart on the paint device [painter].
        *painter: QPainter
        '''
        painter.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing )
        self._axis.paint( painter )

        cols = self.model().columnCount()
        painter.save()
        for c in range( cols ):
            style = self.columnStyle( c )
            painter.setPen( style.pen() )               
            painter.setBrush( style.brush() )
            self._paintValues( painter, c )
        painter.restore()
        self._paintLegend(painter)
        font = self.font()
        font.setItalic( True )
        painter.setFont( font )
        painter.drawText( self._titleRect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, self._title )

        painter.drawRect( self._axis._valuesRect )
        painter.drawRect( self._axis._chartRect )
        painter.drawRect( self._titleRect )
        painter.drawRect( self._legendRect )


    def _paintColumnLegend(self, painter, c, pos, metricsH):
        r = QRect( pos.x() + 25, pos.y() - 15, 30, 30 )
        posText = pos + QPoint( 45, metricsH/2 )
        style = self.columnStyle(c)
        s = str(self.model().headerData( c, Qt.Horizontal ))
        painter.drawText( posText, s )
        painter.save()
        painter.setPen( style.pen() )
        painter.setBrush( style.brush() )
        painter.drawPie( r, 210 * 16, -60 * 16 )
        painter.restore()



    def _paintValues( self, painter, column ):
        rows = self.model().rowCount()
        painter.save()
        isActive = False 
        selectedIndexes = self.selectionModel().selectedIndexes()
        if selectedIndexes != []:
            for idx in selectedIndexes:
                if idx.column() == column:
                    isActive = True
                    break
        else:
            isActive = True
        for r in range(0, rows):
            index = self.model().index( r, column )
            painter.save()
            if len( selectedIndexes ) != 0:
                if index not in selectedIndexes:
                    if isActive == False:
                        c = QColor(Color.Gray)
                        c.setAlpha( 125 )
                        pen = painter.pen()
                        pen.setColor( c )
                        painter.setPen( pen )
                        c = QColor(Color.LightGray)
                        c.setAlpha( 150 )
                        painter.setBrush( QBrush( c ) )
                    else:
                        pen = painter.pen()
                        c = pen.color()
                        c.setAlpha( c.alpha() * 0.5 )
                        pen.setColor( c )
                        painter.setPen( pen )
                        brush = painter.brush()
                        c = brush.color()
                        c.setAlpha( c.alpha() * 0.5 )
                        brush.setColor( c )
                        painter.setBrush( brush )
            path = self.itemPath( index )
            painter.drawPath( path )
            painter.restore()
        painter.restore()


    def _updateRects(self):
        if self.model() == None:
            return None
        self._axis.setModel( self.model() )
        self.scan()
        self.defineRects()
        w = min( self._axis._chartRect.width(), self._axis._chartRect.height() )
        self._axis._valuesRect = QRect( -w/2, -w/2, w, w )
        self._axis._valuesRect.translate( self._axis._chartRect.center().x(), self._axis._chartRect.center().y() )
        self._titleRect.moveTo( self._axis._chartRect.bottomLeft() )
        self._titleRect.translate( (self._axis._chartRect.width() - self._titleRect.width())/2, 10 )
        self._axis._valuesRect = self._axis._valuesRect
        self._axis._chartRect = self._axis._chartRect
        self._axis.update()