from ..Global import Color, Type
from .Chart import Chart, ChartStyle
from .Delegates import PointDelegate, BarDelegate
from .Axis import OrthogonalAxis, AxisView

from PySide.QtGui import QPainter, QPen, QStyleOptionViewItem, QColor, QFontMetrics, QLinearGradient, QBrush, QStyle, QPainterPath, QFont
from PySide.QtCore import QSize, QRect, QPointF, QPoint, Qt, QLineF, QModelIndex, QRectF

class LinearChart(Chart):
    ''' LinearChart class provides a view for QAbstractItemModel to display data in each column as line chart or bar chart.
    To each column in the model corresponds a serie of data.
    '''


    def __init__(self, parent=None):
        ''' Constructor. Constructs an instance with the given 'parent'.
        '''
        super(LinearChart, self).__init__( parent )
        #self._test.origin = QPointF(20, 10)
        self._test = OrthogonalAxis()
        self._axis = AxisView()
        self._pointDelegate = PointDelegate( self )
        self._barDelegate = BarDelegate( self )
        self._minBottomMargin = 0


    def _barStyleColumns(self):
        '''Returns the list of column with the type Bar. Used to calculate the width of each bar.
        See Marb.Global.Type and setColumnType(), columnType()
        '''
        bars = []
        for c in range( 0, self.model().columnCount() ):
            if self.columnType( c ) == Type.Bar:
                bars.append( c )
        return bars


    def _calculateOrderedColumn(self):
        '''Calculates in which order the view should paint the series of data.
        '''
        bars = []
        lines = []
        points = []
        for c in range(0, self.model().columnCount()):
            t = self.columnType(c)
            if t | Type.Bar == t:
                bars.append(c)
            elif t | Type.Line == t:
                lines.append(c)
            else:
                points.append( c )
        return bars + lines + points


    def columnType(self, column):
        '''Returns the type for the given column.
        See Marb.Global.Type and setColumnType()
        '''
        if column in self._style:
            return self._style[ column ].type()
        return ChartStyle().type()


    def itemRect(self, index ):
        '''Reimplemented from Chart.itemRect()
        '''
        r = QRectF()

        t = self.columnType( index.column() )
        value = index.data()
        if value == None:
            return QRect()
        pos = self._axis.valueToPoint( value, index.row() )
        orderedColumns = self._calculateOrderedColumn()
        if t == Type.Bar:
            bars = self._barStyleColumns()
            w = float( self._axis.stepSize() ) / len(bars)
            pos += QPointF( w * orderedColumns.index( index.column() ), 0 )
            br = QPointF( pos.x() + w, self._axis.origin().y() )
            r = QRectF( pos, br )
            if value < 0:
                r.translate( 0, 1 )
            else:
                r.translate( 0, -2 )
        else:
            r = QRectF( -5, -5, 10 ,10 ).translated( pos.x(), pos.y() ) 
        return r.normalized().toRect()


    def paintChart(self, painter):
        painter.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing )
        # self._test.paint( painter, labels )
        ordered = self._calculateOrderedColumn()
        for c in ordered:
            self._paintValues( painter, c )
        # self._paintTextAxis(painter)
        # self._paintLegend(painter)
        # font = self.font()
        # font.setItalic( True )
        # painter.setFont( font )
        painter.drawText( self._titleRect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, self._title )
        self._axis.paint( painter )


    def _paintColumnLegend(self, painter, c, pos, metricsH):
        p1 = pos + QPoint( 10, - metricsH/2 )
        p2 = pos + QPoint( 40, - metricsH/2 )
        posText = pos + QPoint( 45, 0 )
        s = str(self.model().headerData( c, Qt.Horizontal ))
        style = self.columnStyle(c)
        t = style.type()
        painter.drawText( posText, s )
        painter.save()
        painter.setPen( style.pen() )
        if t | Type.Line == t:
            painter.drawLine( p1, p2 )
        if t == Type.Bar:
            option = QStyleOptionViewItem()
            j = 0
            for i in (15, 8, 17, 5 ):
                painter.setPen( Qt.NoPen )
                painter.setBrush( style.brush() )
                r = QRect( 10 + pos.x() + j * 8, pos.y() - i, 5, i )
                painter.drawRect( r )
                j += 1          
        elif t | Type.Point == t:
            option = QStyleOptionViewItem()
            option.rect = QRect( p1.x() + abs(p1.x() - p2.x())/2 - 5, p1.y() - 5, 10, 10 )
            self._pointDelegate.paint( painter, option, self.model().index(0,c) )
        painter.restore()


    def _paintTextAxis(self, painter):
        '''Paints text on the X & Y axis.
        '''
        return None
        painter.save()
        metrics = QFontMetrics( self.font() )
        h = metrics.height()
        textPos = QPoint( h/2 , self._test.origin.y() + 5 );
        x = self._test.xStep + self._test.origin.x()
        i = 0
        
        while (i < self.model().rowCount() ):
            p1 = QPoint( x, self._test.origin.y() - 3 )
            s = str(self.model().headerData( i, Qt.Vertical ))
            painter.save()
            painter.setPen( QPen( QColor(Color.DarkGray), 1.5 ) )
            if self._test.verticalLabel == True:
                painter.rotate( -90 )
                if self._test.dataStartonYAxis == False:
                    painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() - self._test.xStep/2.0 )
                else:
                    painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() - self._test.xStep + h )
                painter.drawText( 0, 0, s )
            else:
                if self._test.dataStartonYAxis == False:
                    painter.drawText( p1.x() - self._test.xStep/2.0 - metrics.width( s )/2.0, textPos.y() + h, s )
                else:
                    painter.drawText( p1.x() - self._test.xStep, textPos.y() + h, s )
            painter.restore()
            i += 1
            x += self._test.xStep
        y = self._test.minBound
        while y <= self._test.maxBound:
            p1 = QPoint( self._test.origin.x(), self._test.valueToPoint(y) )
            s = str(round(y, self._test.nbDigits))
            s = s.rstrip("0")
            s = s.rstrip(".")
            r = QRect( QPoint( 0, p1.y() - h/2 ), QSize( self._test.origin.x() - 5 ,h) )
            painter.drawText( r, Qt.AlignRight, s )
            y += self._test.tickSize
        painter.restore()


    def _paintValues(self, painter, column):
        t = self.columnType(column)
        delegate = None
        if t | Type.Point == t:
            delegate = self._pointDelegate
        elif t == Type.Bar:
            delegate = self._barDelegate
        rows = self.model().rowCount()
        painter.save()
        style = self.columnStyle( column )
        painter.setBrush( style.brush() )
        painter.setPen( style.pen() )
        isActive = True
        if self.selectionModel() != None:
            selectedIndexes = self.selectionModel().selectedIndexes()
            if len( selectedIndexes ) != 0:
                isActive = False
                for idx in selectedIndexes:
                    if idx.column() == column:
                        isActive = True
                        break
        for r in range( rows ):
            painter.setBrush( Qt.red )
            painter.drawRect( self.itemRect( self.model().index( r, column ) ) )
            # index = self.model().index( r, column )
            # option = QStyleOptionViewItem()
            # value = 0
            # try: 
            #     value = float( index.data() )
            # except:
            #     value = 0

            # if value < 0:
            #     option.decorationPosition = QStyleOptionViewItem.Bottom
            # else:
            #     option.decorationPosition = QStyleOptionViewItem.Top
            # if isActive == False:
            #     option.state = QStyle.State_Off
            # elif index in self.selectionModel().selectedIndexes():
            #     option.state = QStyle.State_Selected
            # option.rect = self.itemRect( index )
            # if t | Type.Line == t:
            #     if r < (rows - 1):
            #         if isActive == False:
            #             p1 = option.rect.center()
            #             p2 = self.itemRect( self.model().index( r + 1, column ) ).center()
            #             line = QLineF( p1, p2 )
            #             l = QLineF( line.pointAt( 0.5 ), line.p2() ).normalVector()
            #             l.setLength( 4 )
            #             gradient = QLinearGradient( l.p1(), l.p2() )
            #             c = QColor( Qt.darkGray )
            #             c.setAlpha( 50 )
            #             gradient.setColorAt( 0, c )
            #             gradient.setColorAt( 1, Qt.transparent )
            #             gradient.setSpread( QLinearGradient.ReflectSpread )
            #             painter.save()
            #             pen = QPen( QBrush( gradient ), 8 )
            #             painter.setPen( pen ) 
            #             painter.drawLine( p1, p2 )
            #             painter.restore()
            #         else:
            #             p1 = option.rect.center()
            #             p2 = self.itemRect( self.model().index( r + 1, column ) ).center()
            #             painter.drawLine( p1, p2 )
            # if delegate != None:
            #     delegate.paint( painter, option, index )
        painter.restore()


    def process( self ):
        if self.model() == None:
            return None
        self._axis.setModel( self.model() )
        self._min = 0
        self._max = 0
        self._minBottomMargin = self._scanValues() + 10
        self._updateRects()


    def _updateRects(self):
        if self.model() == None:
            return None
        self.defineRects()
        metrics = QFontMetrics( self.font() )
        self._test.calculateBounds()
        self._test.origin.setX( metrics.width( str(-1 * self._test.order) ) + metrics.width("0") * self._test.nbDigits + self._marginX )
        self._valuesRect = QRect( self._chartRect )
        self._valuesRect.setX( self._test.origin.x() )
        self._test.xStep = float( self._valuesRect.width() ) / ( self.model().rowCount() )
        metrics = QFontMetrics( self.font() )
        length = 0
        for i in range( self.model().rowCount() ):
            s = str(self.model().headerData( i, Qt.Vertical ))
            length = max( length, metrics.width( s ) )

        self._test.verticalLabel = (length > self._test.xStep)
        self._test.axisPos = self._valuesRect.topLeft()
        self._test.setAlphaBeta( self._valuesRect.height() - 20 )
        delta = self._valuesRect.bottom() - ( self._test.origin.y() + self._minBottomMargin )
        if delta < 0:
            self._valuesRect.setHeight( self._valuesRect.height() + delta )
            self._test.setAlphaBeta( self._valuesRect.height() - 20 )
        self._test.xAxisLength = self._valuesRect.width()

        self._titleRect.moveTo( self._chartRect.bottomLeft() )
        self._titleRect.translate( (self._chartRect.width() - self._titleRect.width())/2, 20 )

        self._axis._valuesRect = self._valuesRect
        self._axis._chartRect = self._chartRect
        self._axis.update()


