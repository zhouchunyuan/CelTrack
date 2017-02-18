from PIL import Image,ImageGrab
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from CelTrackControls import ThresholdControl
import sys
import numpy as np
import cv2

# capture area, updated by Capframe::paintEvent
CAP_RECT = QRect()
TRK_POINT = QPoint()
TRKed_CONTOUR = None #the tracked contour
SIG_STOP = False
SIG_ACT = False # used in DoCapture()
SIG_IS_TRACKED = False # if tracking success

WIN_MOUSE_POINT = None
WIN_ZOOM = 1.0

THRESH_LO = 80
THRESH_HI = 255

MOV_X = 0 # x steps to move
MOV_Y = 0 # y steps to move

########################################
#
# excute macro to NIS-Elements
# used as thread "thread.start_new_thread(DoMacro,())"
#
########################################
def DoMacro():
    global MOV_X,MOV_Y,SIG_STOP
    while not SIG_STOP:
        nis = r'"c:\Program Files\NIS-Elements\nis_ar.exe"'
        cmdstr = nis+' -c '+r'StgMoveXY('+str(MOV_X)+','+str(MOV_Y)+',1);'
        #call(cmdstr,shell=True)
        #print cmdstr

        
########################################
#
# This Class is to define a screen area
# using mouse drag and draw
# left click to define topleft and bottomright
# right click to exit GUI
# output : sef.frm as rectangle
#
########################################
class Capframe(QWidget):
    
    def __init__(self,parent=None):
        super(Capframe,self).__init__(parent)
        #The frame area
        self.frm = QRect()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)
        self.showMaximized()
        
    def mousePressEvent(self,event):
        global SIG_ACT
        if event.button()==Qt.LeftButton: 
            self.frm.setTopLeft( QPoint(event.x(), event.y()))
            event.accept()
        if event.button()==Qt.RightButton:
            SIG_ACT = True # start recording
            self.close() 
    
    def mouseMoveEvent(self,event): 
        if event.buttons() & Qt.LeftButton: 
            self.frm.setBottomRight( QPoint(event.x(), event.y()))
            event.accept()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        pen = QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(self.frm)
        qp.end()        
        self.update()

        global CAP_RECT
        CAP_RECT = self.frm

#############################################
#
# This is the control panel GUI
#
#############################################
class TrkPanel(QtGui.QWidget):
    
    def __init__(self):
        super(TrkPanel, self).__init__()

        self.qbtnStt = QtGui.QPushButton()
        self.qbtnStp = QtGui.QPushButton()
        self.qbtnExt = QtGui.QPushButton()

        #self.thresh_lo = QtGui.QLineEdit()

        self.initUI()

    def setLoValue(self,v):
        global THRESH_LO
        THRESH_LO = v

    def setHiValue(self,v):
        global THRESH_HI
        THRESH_HI = v

    def setZoom(self,z):
        global WIN_ZOOM
        WIN_ZOOM = float(z)/100

       
    def initUI(self):
        
        self.threshold = ThresholdControl(THRESH_LO,THRESH_HI)
        self.threshold.valueLoChanged.connect(self.setLoValue)
        self.threshold.valueHiChanged.connect(self.setHiValue)

        self.zoomSld  = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.zoomSld .setFocusPolicy(QtCore.Qt.NoFocus)
        self.zoomSld .setRange(10, 200)#10%-200%
        self.zoomSld .setValue(100)
        self.zoomSld .valueChanged[int].connect(self.setZoom)
        
        self.qbtnStt = QtGui.QPushButton('Define Area', self)
        self.qbtnStt.clicked.connect(self.capScreen)
        self.qbtnStp = QtGui.QPushButton('freeze/start', self)
        self.qbtnStp.clicked.connect(self.record)
        self.qbtnExt = QtGui.QPushButton('Exit', self)
        self.qbtnExt.clicked.connect(self.stopAndExit)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        #add customized threshold control
        grid.addWidget(self.threshold)
        #add zoom control for live window
        grid.addWidget(self.zoomSld)
        grid.addWidget(self.qbtnStt)
        grid.addWidget(self.qbtnStp)
        grid.addWidget(self.qbtnExt)
        #grid.addWidget(qbtn,2,1)
        self.setLayout(grid)
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Tracking Consol')    
        self.show()


    def capScreen(self):
        self.recorder = Capframe()
        
    def record(self):
        global SIG_ACT
        SIG_ACT = not SIG_ACT

    def stopAndExit(self):
        global SIG_STOP
        SIG_STOP = True
        self.close()

#######################################
#
# tool function 
# get center x,y from contour
#
#######################################
def getCenter(contour):
    M = cv2.moments(contour)
    cx0 = int(M['m10']/M['m00'])
    cy0 = int(M['m01']/M['m00'])
    return cx0,cy0
#######################################
#
# capture screen area as video
# and track it
#
#######################################
def DoCapture():
    global CAP_RECT,MOV_X,MOV_Y,SIG_ACT,SIG_STOP,SIG_IS_TRACKED

    while not SIG_STOP:
        capArea = CAP_RECT
        #print capArea.getCoords(),SIG_ACT
        if SIG_ACT and CAP_RECT.width()>0 and CAP_RECT.height()>0:
            
            img = ImageGrab.grab(capArea.getCoords()) #bbox specifies specific region (bbox= x,y,width,height *starts top-left)
            img_np = np.array(img) #this is the array obtained from conversion
            #img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

            #blur
            #img_np = cv2.blur(img_np,(3,3))

            #sharpen
            #kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
            #img_np = cv2.filter2D(img_np, -1, kernel)
            
            imgray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            
            ret,thresh = cv2.threshold(imgray,THRESH_LO,THRESH_HI,cv2.THRESH_TOZERO_INV)

            ##use a 3x3 kernel to get rid of small objects
            ## iteration number is important
            #kernel = np.array([[1,1,1],[1,1,1],[1,1,1]])
            kernel = np.ones((5,5),np.uint8)
            #thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel,iterations=3)
            
            thresh = cv2.dilate(thresh,kernel,iterations = 3)
            thresh = cv2.erode(thresh,kernel,iterations = 3)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel,iterations = 1)

            #gray = np.float32(gray)

            im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_np, contours, -1, (0,255,0), 3)

            
            if len(contours) >0:
                if not SIG_IS_TRACKED :
                    TRKed_CONTOUR = contours[0]
                    SIG_IS_TRACKED = True

                cx0,cy0 = getCenter(TRKed_CONTOUR)

                d2 = sys.maxint    
                for cnt in contours:
                    cx,cy = getCenter(cnt)
                    #cv2.circle(img, (cx,cy), 10, (0,255,255), -1)
                    d = (cx-cx0)*(cx-cx0)+(cy-cy0)*(cy-cy0)
                    
                    if d2 >= d:
                        d2 = d
                        TRKed_CONTOUR = cnt
                        TRK_POINT = QPoint(cx,cy)

                if d2 == sys.maxint:
                    SIG_IS_TRACKED = False
                if SIG_IS_TRACKED:
                    cv2.circle(img_np, (TRK_POINT.x(),TRK_POINT.y()), 10, (0,0,255), -1)
                    hull = cv2.convexHull(TRKed_CONTOUR)
                    cv2.drawContours(img_np, [hull], 0, (255,0,0), 3)
            if len(contours) == 0:
                    TRKed_CONTOUR = None
                    SIG_IS_TRACKED = False       
            img = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)


            #cv2.imshow('img',img)
            imshowScale('img',img,WIN_ZOOM)
            
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                SIG_STOP=True
                break
            elif k == ord(' '):
                # to switch tracking objs
                totCnt = len(contours)
                if totCnt >1 and SIG_IS_TRACKED:
                    for i in range(totCnt):
                        if cv2.moments(contours[i]) == cv2.moments(TRKed_CONTOUR):
                            if i == totCnt-1: #the last obj in array
                                TRKed_CONTOUR = contours[0]
                            else :
                                TRKed_CONTOUR = contours[i+1]
                            break

            # start define tracking obj by mouse xy
            if WIN_MOUSE_POINT is not None:
                d = sys.maxint
                
                for cnt in contours :
                    xm = WIN_MOUSE_POINT.x()
                    ym = WIN_MOUSE_POINT.y()
                    xc,yc = getCenter(cnt)
                    xc = xc*WIN_ZOOM
                    yc = yc*WIN_ZOOM
                    ref = (xc-xm)*(xc-xm)+(yc-ym)*(yc-ym)
                    if d > ref :
                        d = ref
                        TRKed_CONTOUR = cnt
                        SIG_IS_TRACKED = True

    #cv2.destroyAllWindows()

##########################################
#
# show zoomed image window
# percent : a float number, 1.0 = 100%
#
##########################################
def imshowScale(title,image,percent):
    # we need to keep in mind aspect ratio so the image does
    # not look skewed or distorted -- therefore, we calculate
    # the ratio of the new image to the old image
    size = image.shape # [1] is x, [0] is y
    dim = (int(size[1]*percent), int(size[0]*percent))
     
    # perform the actual resizing of the image and show it
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    #cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.imshow(title, resized)
    #setup call back function
    cv2.setMouseCallback(title, click_on_img)
#######################################
#
# callback function
# from cv2.imshow()
#
#######################################
def click_on_img(event, x, y, flags, param):
    global WIN_MOUSE_POINT
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        WIN_MOUSE_POINT = QPoint(x, y)

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        WIN_MOUSE_POINT = None
    
 

		
###########################################
#
# Application Class to start QT GUI
#
###########################################
class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.main = TrkPanel()
        self.main.show()
    def run(self):
        self.exec_()

        



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    f = Capframe()
    sys.exit(app.exec_())


