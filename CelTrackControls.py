import sys
from PyQt4 import QtGui, QtCore

# original example: http://blog.csdn.net/ozuijiaoweiyang/article/details/44102699
class ThresholdControl(QtGui.QWidget):

    #define signals
    valueHiChanged = QtCore.pyqtSignal(int)
    valueLoChanged = QtCore.pyqtSignal(int)
    rightButtonClick = QtCore.pyqtSignal()

    def __init__(self, vL = 0, vH = 255):      
        super(ThresholdControl, self).__init__()
        self.MAX = 255
        self.valueLo = vL
        self.valueHi = vH

        self.cursor_lo = 0
        self.cursor_hi = 0

        # display handle for threshold cursor or not
        self.showHandleLo = False
        self.showHandleHi = False
        self.hw = 3 # handle half width

        # for mouse drag threshold
        # used in mouseMove event
        self.dragLo = False
        self.dragHi = False
        
        self.initUI()
        # enable 'mouseMove' event without press
        self.setMouseTracking(True)

    def initUI(self):

        self.setMinimumSize(1, 30)

        self.num = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250]
        
    def setValueLo(self, valueLo):
        if valueLo >=0 and valueLo <self.valueHi:
          self.valueLo = valueLo
          # emit signal
          self.valueLoChanged.emit(self.valueLo)
        self.repaint()

    def setValueHi(self, valueHi):
        if valueHi > self.valueLo and valueHi <= self.MAX:
          self.valueHi = valueHi
          self.valueHiChanged.emit(self.valueHi)
        self.repaint()

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
        
    def mouseMoveEvent(self, e):

        w = self.size().width()

        x = float(e.x())

        if self.cursor_lo > x-self.hw and self.cursor_lo < x+self.hw :
          self.showHandleLo = True

        elif self.cursor_hi > x-self.hw and self.cursor_hi < x+self.hw :
          self.showHandleHi = True

        else:
          self.showHandleLo = False
          self.showHandleHi = False

        #drag cursor
        if self.dragLo:
          self.setValueLo(x/w*self.MAX)
        if self.dragHi:
          self.setValueHi(x/w*self.MAX)

        self.repaint()
        
    def mousePressEvent(self, e):
        if e.button()==QtCore.Qt.LeftButton:
          if self.showHandleLo == True:
            self.dragLo = True
          elif self.showHandleHi == True:
            self.dragHi = True
          else:
            self.dragLo = False
            self.dragHi = False
            
        if e.button()==QtCore.Qt.RightButton:
            self.rightButtonClick.emit()# use right click to trigger thresh image

        
    def mouseReleaseEvent(self, e):
        self.dragLo = False
        self.dragHi = False


    def drawWidget(self, qp):

        size = self.size()
        w = size.width()
        h = size.height()

        font = QtGui.QFont('Serif', int(w/55), QtGui.QFont.Light)
        qp.setFont(font)
        
        #step = int(round(w / self.MAX))
        step = float(w) / self.MAX

        self.cursor_lo = int(self.valueLo*step)
        self.cursor_hi = int(self.valueHi*step)
         
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(QtGui.QColor(255, 255, 184))
        qp.drawRect(0, 0, self.cursor_lo, h)
        
        qp.setPen(QtGui.QColor(255, 175, 175))
        qp.setBrush(QtGui.QColor(255, 175, 175))
        qp.drawRect(self.cursor_lo, 0, self.cursor_hi, h)

        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(QtGui.QColor(255, 255, 184))
        qp.drawRect(self.cursor_hi, 0, w, h)


        pen = QtGui.QPen(QtGui.QColor(20, 20, 20), 1, 
            QtCore.Qt.SolidLine)

        qp.setPen(pen)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.drawRect(0, 0, w-1, h-1)

        j = 0
        for n in self.num:
            qp.drawLine(n*step, 0, n*step, 5)
            metrics = qp.fontMetrics()
            fw = metrics.width(str(self.num[j]))
            qp.drawText(n*step-fw/2, h/2, str(self.num[j]))
            j = j + 1
            
        # must put at last, or will be blocked by other drawing
        qp.setBrush(QtGui.QColor(255, 255, 184))
        if self.showHandleLo :
          qp.drawRect(self.cursor_lo-self.hw, h/2-4, self.hw*2, 8)
        if self.showHandleHi :
          qp.drawRect(self.cursor_hi-self.hw, h/2-2, self.hw*2, 8)

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):      

        sld_lo = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld_lo.setFocusPolicy(QtCore.Qt.NoFocus)
        sld_lo.setRange(0, 255)
        sld_lo.setValue(25)
        sld_lo.setGeometry(30, 40, 150, 30)

        sld_hi = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld_hi.setFocusPolicy(QtCore.Qt.NoFocus)
        sld_hi.setRange(0, 255)
        sld_hi.setValue(100)
        sld_hi.setGeometry(30, 50, 150, 40)

        #self.c = Communicate()        
        self.wid = ThresholdControl(sld_lo.value(),sld_hi.value())
        #signal
        self.wid.valueLoChanged.connect(sld_lo.setValue)
        self.wid.valueHiChanged.connect(sld_hi.setValue)
        #self.c.updateLo[int].connect(self.wid.setValueLo)
        #self.c.updateHi[int].connect(self.wid.setValueHi)

        sld_lo.valueChanged[int].connect(self.changeValueLo)
        sld_hi.valueChanged[int].connect(self.changeValueHi)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setGeometry(300, 300, 390, 210)
        self.setWindowTitle('Burning widget')
        self.show()

    def changeValueLo(self, value):

        #self.c.updateLo.emit(value)
        self.wid.setValueLo(value)
        self.wid.repaint()
        
    def changeValueHi(self, value):

        #self.c.updateHi.emit(value)
        self.wid.setValueHi(value)
        self.wid.repaint()


def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
