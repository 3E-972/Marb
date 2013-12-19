import Marb
from Marb.Charts import *

from PySide.QtGui import *
from PySide.QtCore import *
from PySide import QtCore

import sys
import random 

from Marb.Delegates.PercentDelegate import RoundedPercentDelegate

app = QApplication(sys.argv)

model = QStandardItemModel( 3, 2 )
for i in range( 0, model.rowCount() ):
    for j in range( 0, model.columnCount() ):
        #model.setData( model.index( i, j ), random.randint(1, 15) )
        model.setData( model.index( i, j ), 1 + j )

model.setHeaderData( i, Qt.Vertical, "test plus long" )
# chart = RadarChart()
# chart.setModel( model )
# chart.show()

# chart1 = RadialChart()
# chart1.setModel( model )
# chart1.show()

chart2 = LinearChart()
style = chart2.columnStyle( 1 )
style.setType( Marb.Type.Bar )
chart2.setColumnStyle( 1, style )
chart2.setModel( model )
chart2.show()

app.exec_()
