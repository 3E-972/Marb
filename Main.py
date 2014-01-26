import Marb
from Marb.Charts import *

from PySide.QtGui import *
from PySide.QtCore import *
from PySide import QtCore

import sys
import random 

from Marb.Delegates.PercentDelegate import RoundedPercentDelegate

app = QApplication(sys.argv)

model = QStandardItemModel( 10, 5 )
for i in range( 0, model.rowCount() ):
    
    for j in range( 0, model.columnCount() ):
        v = random.randint(-10, 10)
        model.setData( model.index( i, j ), v )
    model.setHeaderData( i, Qt.Vertical, "test plus long" )
model.setData( model.index( i, j ), 1 )
# model.setHeaderData( i, Qt.Vertical, "test plus long" )
# chart = RadarChart()
# chart.setModel( model )
# chart.show()

chart1 = LinearChart()
chart1.setModel( model )
chart1.show()
chart1.setTitle( "Title" )
style = chart1.columnStyle( 1 )
style.setType( Marb.Type.Bar )
chart1.setColumnStyle( 1, style )
style = chart1.columnStyle( 0 )
style.setType( Marb.Type.Bar )
chart1.setColumnStyle( 0, style )

# chart2 = LinearChart()
# chart2.setTitle( "my title" )
# style = chart2.columnStyle( 1 )
# style.setType( Marb.Type.Bar )
# chart2.setColumnStyle( 1, style )
# style = chart2.columnStyle( 0 )
# style.setType( Marb.Type.Bar )
# chart2.setColumnStyle( 0, style )
# chart2.setModel( model )
# chart2.show()

app.exec_()
