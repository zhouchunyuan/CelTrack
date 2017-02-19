import sys
from PyQt4 import QtGui, QtCore
import thread
import cv2 
import numpy as np

th1=0
th2=255
# original example: http://blog.csdn.net/ozuijiaoweiyang/article/details/44102699
class ThresholdControl(QtGui.QWidget):

    #define signals
    valueHiChanged = QtCore.pyqtSignal(int)
    valueLoChanged = QtCore.pyqtSignal(int)

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
        sld_lo.setValue(200)
        sld_lo.setGeometry(30, 40, 150, 30)

        sld_hi = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld_hi.setFocusPolicy(QtCore.Qt.NoFocus)
        sld_hi.setRange(0, 255)
        sld_hi.setValue(255)
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
        global th1
        th1 = value
        
    def changeValueHi(self, value):

        #self.c.updateHi.emit(value)
        self.wid.setValueHi(value)
        self.wid.repaint()
        global th2
        th2 = value
        
def detectCorner(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    corners = cv2.goodFeaturesToTrack(gray,200,0.01,10)
    if corners is not None:
        corners = np.int0(corners)

        for corner in corners:
            x,y = corner.ravel()
            cv2.circle(img, (x,y), 3, 255, -1)
            
def detectContour(img,th1,th2):
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ## equalize the histogram of the input image
    ## does not work well
    #imgray = cv2.equalizeHist(imgray)

    ##get threshold
    ##be sure to use THRESH_BINARY_INV to track the dark worms
    #ret,thresh = cv2.threshold(imgray,th1,th2,cv2.THRESH_BINARY_INV)
    ret,thresh = cv2.threshold(imgray,th1,th2,cv2.THRESH_TOZERO_INV)

    ##use a 3x3 kernel to get rid of small objects
    ## iteration number is important
    #kernel = np.array([[1,1,1],[1,1,1],[1,1,1]])
    kernel = np.ones((5,5),np.uint8)
    #thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel,iterations=3)
    
    thresh = cv2.dilate(thresh,kernel,iterations = 3)
    thresh = cv2.erode(thresh,kernel,iterations = 3)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel,iterations = 1)

    #gray = np.float32(gray)

#    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    #cv2.drawContours(img, contours, -1, (0,255,0), 3)
    if len(contours)>0:
        points = contours[0]
        #for p in points:
        #    cv2.circle(img, (p[0][0],p[0][1]), 3, (0,255,255), -1)



        L = len(points)

        if L>30 :
            angleMin = 0
            tail_x = 0
            tail_y = 0
            d = 4
            for i in range(0,L):
                p0 = points[i][0]
                x,y = p0[0],p0[1]
                x1,y1 = x,y
                x2,y2 = x,y
                if i < d:
                    p = points[L-d+i][0]
                    x1,y1 = p[0],p[1]
                    p = points[i+d][0]
                    x2,y2 = p[0],p[1]
                elif i > L-d-1:
                    p = points[i-d][0]
                    x1,y1 = p[0],p[1]
                    p = points[L-i+d-1][0]
                    x2,y2 = p[0],p[1]
                else:
                    p = points[i-d][0]
                    x1,y1 = p[0],p[1]
                    p = points[i+d][0]
                    x2,y2 = p[0],p[1]
                #a1 = np.angle(complex(x-x1,y-y1),1)
                #a2 = np.angle(complex(x2-x,y2-y),1)
                #a = 360+a2-a1
                a = complex(x-x1,y-y1)
                b = complex(x2-x,y2-y)
                c = (np.vdot(a,b)/(abs(a)*abs(b))).real
                if c>1 :
                    c = 1
                if c<-1:
                    c = -1
                angle = np.arccos(c)
                if angleMin < angle:
                    angleMin = angle
                    tail_x = p0[0]
                    tail_y = p0[1]
                    
                
                #cv2.circle(img, (p0[0],p0[1]), 3, (0,angle/np.pi*255,255), -1)
                if angle > np.pi*0.4:
                    cv2.circle(img, (p0[0],p0[1]), 3, (0,255,255), -1)
                cv2.circle(img, (tail_x,tail_y), 3, (0,255,0), -1)
        

                
def capture():
    global th1,th2
    # capture frames from a camera
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('C. elegans movement.mp4')
    cap.set(1,300)# CV_CAP_PROP_POS_FRAMES 0-based index of the frame to be decoded/captured next.
     
    # loop runs if capturing has been initialized
    while(1):
     
        # reads frames from a camera
        ret, frame = cap.read()

        detectContour(frame,80,200)
        
        #detectCorner(frame)
        
        #kernel_sharpen = np.array([[1,1,1], [1,-7,1], [1,1,1]])
        kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        frame = cv2.filter2D(frame, -1, kernel_sharpen)
        
        #edges = cv2.Canny(frame,th1,th2)
     
        # Display edges in a frame
        #cv2.namedWindow('Edges',cv2.WINDOW_NORMAL)
        cv2.namedWindow('origin',cv2.WINDOW_NORMAL)
        #cv2.imshow('Edges',edges)
        cv2.imshow('origin',frame)
     
        # Wait for Esc key to stop
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
     
    # Close the window
    cap.release()
     
    # De-allocate any associated memory usage
    cv2.destroyAllWindows() 

def main():

    thread.start_new_thread(capture,())
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
