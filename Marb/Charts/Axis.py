from PySide.QtGui import QPainter, QPen, QColor, QFontMetrics, QPainterPath, QBrush, QFont
from PySide.QtCore import QSize, QRect, QPointF, QPoint, Qt, QLineF

from ..Global import Color



class Axis:
    def __init__( self, nbTicks = 10, minimum = 0, maximum = 0 ):
        self.min = minimum
        self.max = maximum
        self.nbTicks = nbTicks
        self.minBound = 0
        self.maxBound = 0
        self.order = 1
        self.tickSize = 0
        self.alpha = 1
        self.beta = 1
        self.nbDigits = 1
        self.length = 0
        self.axisPos = QPoint(20,10)
        self.origin = QPoint( 0, 0 )


    def calculateBounds(self):
        '''Calculates the minimum bounds and the maximum bounds (i.e., the minimum and the maximum displayed on the chart).
        Calculates the order and the tick size(delta between two ticks on the Y axis) of the charts values.
        If the minimum is equal to the maximum, the minimum bound is equal to minimum - 1 and the maximum bound to maximum + 1
        '''
        self.minBound = self.min
        self.maxBound = self.max
        if abs(self.maxBound - self.minBound) == 0:
            self.maxBound += 1
            self.minBound -= 1
        self.order = self.calculateOrder( self.max - self.min )
        self.tickSize = (self.max - self.min ) / (self.nbTicks - 1)
        if self.order >= 10:
            self.nbDigits = 0
        elif self.order == 1:
            self.nbDigits = 2
        else:
            nbZero = str(self.order).count( '0' )
            self.nbDigits = nbZero + 2

        self.maxBound += self.order
        self.minBound -= self.order


    def calculateOrder( self, value ):
        '''Calculates the order of scale for value (i.e. the power of ten greater than value).
        '''
        order = 1.0
        v = abs( value )
        if v >= 1:
            while v > 1:
                order *= 10.0
                v /= 10.0
            order /= 10.0
        elif v != 0:
            while v < 1:
                order /= 10.0
                v *= 10.0
            order *= 10.0
        return int(order)


    def setAlphaBeta(self, length):
        '''Calculates the coefficients alpha and beta used to convert a value in the model in the corresponding value in pixel in the chart.
        Translates the origin to place the X-Axis.
        '''
        self.length = length
        ln = length * 0.90
        self.alpha = -float( ln ) / float( self.maxBound - self.minBound )
        #self.beta = (self.maxBound * ln ) / ( self.maxBound - self.minBound ) + self.axisPos.y() + length * 0.1
        self.beta = self.maxBound * -self.alpha + self.axisPos.y() + length * 0.1
        self.origin.setY( self.beta )


    def valueToPoint(self, value):
        '''Converts the given value in pixel according to the chart scale.
        The pixel value is given by the equation: y = alpha * value + beta 
        '''
        try:
            value = float(value)
        except:
            value = 0
        return value * self.alpha + self.beta


    def paint():
        raise( NotImplementedError, "Must be implemented." )



class OrientedAxis( Axis ):
    class _OrientedAxis( Axis ):
        def __init__( self ):
            super( OrientedAxis._OrientedAxis, self ).__init__()
            self.line = QLineF()
            self.pen = QPen( QColor(Color.LightGray), 1.5 )


        def paint( self, painter ):
            painter.save()
            painter.setPen( self.pen )
            painter.drawLine( self.line )
            painter.restore()


        def setP1( self, p1 ):
            self.line.setP1( p1 )


        def setP2( self, p2 ):
            self.line.setP2( p2 )


        def valueToPoint( self, value ):
            e = float( self.max - self.min )
            p = abs( float( value - self.min) / e )
            return self.line.pointAt( p )
    
    def __init__( self ):
        super( OrientedAxis, self ).__init__()
        self.axis = []

    def clear( self ):
        self.axis = []

    def paint( self, painter ):
        for axis in self.axis:
            axis.paint( painter )

    def setP1( self, p1, axisNumber ):
        if len( self.axis ) <= axisNumber:
            #self.axis[ axisNumber ] = OrientedAxis._OrientedAxis()
            for _ in range( len(self.axis) - 1, axisNumber + 1 ):
                self.axis.append( OrientedAxis._OrientedAxis() )
        self.axis[ axisNumber ].setP1( p1 )

    def setP2( self, p2, axisNumber ):
        if len( self.axis ) <= axisNumber:
            #self.axis[ axisNumber ] = OrientedAxis._OrientedAxis()
            for _ in range( len(self.axis) - 1, axisNumber + 1 ):
                self.axis.append( OrientedAxis._OrientedAxis() )
        self.axis[ axisNumber ].setP2( p2 )

    def valueToPoint( self, value, axisNumber ):
        e = float( self.max - self.min )
        p = abs( float( value - self.min) / e )
        return self.axis[ axisNumber].line.pointAt( p )



class OrthogonalAxis(Axis):
    def __init__( self ):
        super( OrthogonalAxis, self ).__init__()
        self.angle = 90.0
        self.angleAxis = -90.0
        self.xAxisLength = 0
        self.pen = QPen( QColor(Color.LightGray), 1.5 )
        self.xStep = 0
        self.valueCount = 1
        self.xAxis = QLineF()
        self.font = QFont()
        self.verticalLabel = False
        self.dataStartonYAxis = True


    def paint( self, painter, labels ):
        painter.save()
        painter.setPen( self.pen )
        line = QLineF( self.origin, self.origin + QPoint(0,10) )
        line.setAngle( self.angle )
        line.setLength( self.length )

        self.xAxis = QLineF( self.origin, self.origin + QPoint(0,10) )
        self.xAxis.setAngle( self.angle + self.angleAxis )
        self.xAxis.setLength( self.xAxisLength )

        painter.drawLine( line )
        self._paintXAxis( painter, labels )
        c = painter.pen().color()
        c.setAlpha( 150 )
        painter.setPen( QPen( c , 1 ) )
        self._paintYAxis( painter )
        painter.restore()


    def _paintXAxis( self, painter, labels ):
        painter.drawLine( self.xAxis )
        n = len( labels )
        i = 0
        metrics = QFontMetrics( self.font )
        h = metrics.height()
        textPos = QPoint( h/2 , self.origin.y() + 5 );
        for i in range( 0, n ):
            s = labels[ i ]
            x = self.xAxis.pointAt( float(i)/float(n) )
            
            l = QLineF( x - QPoint(0, 3), x + QPoint(0, 3) )
            painter.drawLine( l )

            p1 = QPoint( x.x(), self.origin.y() - 3 )           
            
            painter.save()
            painter.setPen( QPen( Qt.darkGray ) )
            if self.verticalLabel == True:
                painter.rotate( -90 )               
                if self.dataStartonYAxis == False:
                    painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() + self.xStep/2.0 )
                else:
                    painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() + h )
                painter.drawText( 0, 0, s )
            else:
                if self.dataStartonYAxis == False:
                    painter.drawText( p1.x() + self.xStep/2.0 - metrics.width( s )/2.0, textPos.y() + h, s )
                else:
                    painter.drawText( p1.x(), textPos.y() + h, s )
            painter.restore()


    def _paintYAxis( self, painter ):
        '''Paints text on the X & Y axis.
        '''
        y = self.minBound
        while y <= self.maxBound:
            p1 = QPoint( self.origin.x(), self.valueToPoint(y) )
            p2 = p1 + QPoint( self.xAxisLength, 0 )
            l = QLineF( p1, p2 )
            (intersectType, intersectionPoint) = l.intersect( self.xAxis )
            if intersectType == QLineF.BoundedIntersection:
                l.setP2( intersectionPoint )
            painter.drawLine( l )
            y += self.tickSize

        painter.save()
        metrics = QFontMetrics( self.font )
        h = metrics.height()
        textPos = QPoint( h/2 , self.origin.y() + 5 );
        x = self.xStep + self.origin.x()
        i = 0

        painter.setPen( QPen( Qt.darkGray ) )

        y = self.minBound
        while y <= self.maxBound:
            p1 = QPoint( self.origin.x(), self.valueToPoint(y) )
            s = str(round(y, self.nbDigits))
            s = s.rstrip("0")
            s = s.rstrip(".")
            r = QRect( QPoint( 0, p1.y() - h/2 ), QSize( self.origin.x() - 5 ,h) )
            painter.drawText( r, Qt.AlignRight, s )
            y += self.tickSize
        painter.restore()




class RadialAxis( Axis ):
    def __init__( self ):
        super( RadialAxis, self ).__init__()
        self.nbTicks = 5
        self.centerHoleDiam = 0
        self.origin = QPointF(0,0)

    def setAlphaBeta( self, length ):
        self.centerHoleDiam = length * 0.2
        m = length * 0.3 
        self.alpha = float( length - m ) / float( self.maxBound - self.minBound )
        self.beta = length - self.alpha * self.maxBound

    def paint(self, painter):
        y = self.minBound
        painter.save()
        c = QColor(Qt.lightGray)
        c.setAlpha( 100 )
        painter.setPen( QPen( c , 2) )
        while y <= self.maxBound:
            v = self.valueToPoint( y )
            rectangle = QRect( -v/2, -v/2, v, v )
            rectangle.translate( self.origin )
            path = QPainterPath()
            path.addEllipse( rectangle )
            painter.drawPath( path )
            y += self.tickSize
        painter.restore()



class AxisView:
    def __init__( self ):
        super( AxisView, self ).__init__()
        self._valuesRect = QRect()
        self._chartRect = QRect()
        self.yAxis = QLineF()
        self.xAxis = QLineF()
        self.font = QFont()


    def setModel( self, model ):
        self.model = model

    def update( self ):
        self.scan()
        self.yAxis = QLineF( self._valuesRect.bottomLeft(), self._valuesRect.topLeft() )
        origin = self.valueToPoint( 0, 0 )
        self.xAxis.setP1( QPoint( self.yAxis.p1().x(), origin.y() ) )
        self.xAxis.setP2( self.xAxis.p1() + QPoint( self._valuesRect.width(), 0 ) )

    def scan( self ):
        '''Scans values in the model to find the minimum and the maximum. Returns the width needed to display the Y scale.
        If the values are greater than zero, the minimum is equal to 0. If the values are less than 0, the maximum is equal to 0.
        If a value is not a number (undefined, a string, etc.), she's considered as equal to 0. 
        '''
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        metrics = QFontMetrics( self.font )
        textWidth = 0
        # value = self.model().index( 0, 0 ).data()
        # try:
        #   value = float(value)
        # except:
        #   value = 0
        _min = 0
        _max = 0
        for r in range( 0, rows ):
            s = str(self.model.headerData( r, Qt.Vertical ))
            textWidth = max( textWidth, metrics.width( s ) + 5 )
            for c in range( 0, cols ):
                value = self.model.index( r, c ).data()
                try:
                    value = float(value)
                except:
                    value = 0
                _min = float(min( _min, value ))
                _max = float(max( _max, value ))
        self.min = _min
        self.max = _max

        self.yLabelsLength = textWidth

    def paint( self, painter ):
        painter.save()
        painter.setPen( QPen( Qt.red, 1 ) )
        painter.drawLine( self.yAxis )
        painter.drawLine( self.xAxis )
        painter.restore()

    def valueToPoint( self, value, axisNumber ):
        e = float( self.max - self.min )
        ratio = abs( float( value - self.min) / e )
        y = self.yAxis.pointAt( ratio ).y()
        ratio = float( axisNumber / (self.model.rowCount() - 1) )
        x = self.xAxis.pointAt( ratio ).x()
        return QPointF( x, y )


    def stepSize( self ):
        return self.xAxis.length() / float( self.model.rowCount() )


    def origin( self ):
        return self.xAxis.p1()

# class OrthogonalAxis(Axis):
#     def __init__( self ):
#         super( OrthogonalAxis, self ).__init__()
#         self.angle = 90.0
#         self.angleAxis = -90.0
#         self.xAxisLength = 0
#         self.pen = QPen( QColor(Color.LightGray), 1.5 )
#         self.xStep = 0
#         self.valueCount = 1
#         self.xAxis = QLineF()
#         self.font = QFont()
#         self.verticalLabel = False
#         self.dataStartonYAxis = True


#     def paint( self, painter, labels ):
#         painter.save()
#         painter.setPen( self.pen )
#         line = QLineF( self.origin, self.origin + QPoint(0,10) )
#         line.setAngle( self.angle )
#         line.setLength( self.length )

#         self.xAxis = QLineF( self.origin, self.origin + QPoint(0,10) )
#         self.xAxis.setAngle( self.angle + self.angleAxis )
#         self.xAxis.setLength( self.xAxisLength )

#         painter.drawLine( line )
#         self._paintXAxis( painter, labels )
#         c = painter.pen().color()
#         c.setAlpha( 150 )
#         painter.setPen( QPen( c , 1 ) )
#         self._paintYAxis( painter )
#         painter.restore()


#     def _paintXAxis( self, painter, labels ):
#         painter.drawLine( self.xAxis )
#         n = len( labels )
#         i = 0
#         metrics = QFontMetrics( self.font )
#         h = metrics.height()
#         textPos = QPoint( h/2 , self.origin.y() + 5 );
#         for i in range( 0, n ):
#             s = labels[ i ]
#             x = self.xAxis.pointAt( float(i)/float(n) )
            
#             l = QLineF( x - QPoint(0, 3), x + QPoint(0, 3) )
#             painter.drawLine( l )

#             p1 = QPoint( x.x(), self.origin.y() - 3 )           
            
#             painter.save()
#             painter.setPen( QPen( Qt.darkGray ) )
#             if self.verticalLabel == True:
#                 painter.rotate( -90 )               
#                 if self.dataStartonYAxis == False:
#                     painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() + self.xStep/2.0 )
#                 else:
#                     painter.translate( -textPos.y() - metrics.width( s ) - 3 , p1.x() + h )
#                 painter.drawText( 0, 0, s )
#             else:
#                 if self.dataStartonYAxis == False:
#                     painter.drawText( p1.x() + self.xStep/2.0 - metrics.width( s )/2.0, textPos.y() + h, s )
#                 else:
#                     painter.drawText( p1.x(), textPos.y() + h, s )
#             painter.restore()


#     def _paintYAxis( self, painter ):
#         '''Paints text on the X & Y axis.
#         '''
#         y = self.minBound
#         while y <= self.maxBound:
#             p1 = QPoint( self.origin.x(), self.valueToPoint(y) )
#             p2 = p1 + QPoint( self.xAxisLength, 0 )
#             l = QLineF( p1, p2 )
#             (intersectType, intersectionPoint) = l.intersect( self.xAxis )
#             if intersectType == QLineF.BoundedIntersection:
#                 l.setP2( intersectionPoint )
#             painter.drawLine( l )
#             y += self.tickSize

#         painter.save()
#         metrics = QFontMetrics( self.font )
#         h = metrics.height()
#         textPos = QPoint( h/2 , self.origin.y() + 5 );
#         x = self.xStep + self.origin.x()
#         i = 0

#         painter.setPen( QPen( Qt.darkGray ) )

#         y = self.minBound
#         while y <= self.maxBound:
#             p1 = QPoint( self.origin.x(), self.valueToPoint(y) )
#             s = str(round(y, self.nbDigits))
#             s = s.rstrip("0")
#             s = s.rstrip(".")
#             r = QRect( QPoint( 0, p1.y() - h/2 ), QSize( self.origin.x() - 5 ,h) )
#             painter.drawText( r, Qt.AlignRight, s )
#             y += self.tickSize
#         painter.restore()