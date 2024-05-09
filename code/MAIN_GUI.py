from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QLabel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import *
from SHIITAKE_GUI_NEW import Ui_MainWindow
from rpi_python_drv8825.stepper import StepperMotor
import RPi.GPIO as GPIO
import time
import sys
import re 
import cv2
import numpy as np
import os
from time import sleep
import csv
import atexit


GPIO.setmode(GPIO.BCM)
widthImg = 512
heightImg = 384
Conveyor_Realy = 27
Bristles_Realy = 22
Motor_Forward_Realy = 5
Motor_Reverse_Realy = 6
Shiitake_Pusher_Top = 23
Shiitake_Pusher_Bottom = 16
Bristles_Top_LS = 17
Bristles_Bottom_LS = 4
DIR = 18
STEP = 24
x = 0
y = 50
w = 5000
h = 100
GPIO.setup(Conveyor_Realy, GPIO.OUT)
GPIO.setup(Bristles_Realy, GPIO.OUT)
GPIO.setup(Motor_Forward_Realy, GPIO.OUT)
GPIO.setup(Motor_Reverse_Realy, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(Shiitake_Pusher_Top, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Bristles_Top_LS, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Bristles_Bottom_LS, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.output(Conveyor_Realy, GPIO.LOW)
GPIO.output(Bristles_Realy, GPIO.LOW)
GPIO.output(Motor_Reverse_Realy, GPIO.LOW)
GPIO.output(Motor_Forward_Realy, GPIO.LOW)







class PyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PyMainWindow, self).__init__()
        self.setupUi(self)       # enables stepper driver
        self.cap = cv2.VideoCapture(0)
        self.pushButton.clicked.connect(self.Shiitake_Pusher_AUTO) #香菇梗推出
        self.pushButton_5.clicked.connect(self.Bristles_Up)  #刷毛上升1mm
        self.pushButton_6.clicked.connect(self.Bristles_Down)  #刷毛下降1mm
        self.pushButton_9.clicked.connect(self.Automatically_Open)  #自動開啟ON
        self.pushButton_10.clicked.connect(self.Automatically_Close) #自動開啟OFF
        self.pushButton_11.clicked.connect(self.Bristles_Realy_Power_On) #刷毛開啟
        self.pushButton_12.clicked.connect(self.Bristles_Realy_Power_Off) #刷毛關閉
        self.pushButton_13.clicked.connect(self.Conveyor_Realy_Power_On) #輸送帶開啟
        self.pushButton_14.clicked.connect(self.Conveyor_Realy_Power_Off) #輸送帶關閉
        self.pushButton_15.clicked.connect(self.Bristles_Auto_On) #自動模式開啟
        self.pushButton_16.clicked.connect(self.Bristles_Auto_Off) #自動模式關閉
        self.area_list = []
        self.length_list = []
        self.effect_list = []
        self.timer_camera = QTimer()
        self.timer_camera.start(30)
        self.timer_camera.timeout.connect(self.show_camera)
        self.Thread_1 = Thread_1()
        self.Thread_2 = Thread_2(self.cap)
        self.Thread_2.avgArea.connect(self.avgAreas)
        self.Thread_2.avgLength.connect(self.avgLengths)
        self.Thread_2.avgEffect.connect(self.avgEffect)
        self.Thread_2.start()
        self.Thread_3 = Thread_3(self.cap)

    def avgEffect(self, effect):
        self.effect_list.append(effect)
        avgEFFECT = float(np.mean(self.effect_list))
        self.textBrowser_6.setText(str(avgEFFECT)+ "個/秒")

    def avgAreas(self, area):
        self.area_list.append(area)
        avgAREA = int(np.mean(self.area_list))
        self.textBrowser_2.setText(str(avgAREA)+ "cm2")

    def avgLengths(self, area):
        self.length_list.append(area)
        avgLENGTH = int(np.mean(self.length_list))
        self.textBrowser_5.setText(str(avgLENGTH)+ "cm")

    def updateFrame(self, image):
        self.label_10.setPixmap(QtGui.QPixmap.fromImage(image))

    def Shiitake_Pusher_AUTO(self):
        self.pushButton.setEnabled(False)
        self.Thread_1 = Thread_1()
        self.Thread_1.singal.connect(self.open_1)
        self.Thread_1.start()

    def open_1(self):
        self.pushButton.setEnabled(True)

    def Conveyor_Realy_Power_On(self):
        GPIO.output(Conveyor_Realy, GPIO.HIGH)
        print("Conveyor_Realy_Power_On")
        time.sleep(0.5)

    def Conveyor_Realy_Power_Off(self):
        GPIO.output(Conveyor_Realy, GPIO.LOW)
        print("Conveyor_Realy_Power_Off")
        time.sleep(0.5)

    def Bristles_Realy_Power_On(self):
        GPIO.output(Bristles_Realy, GPIO.HIGH)
        print("Bristles_Realy_Power_On")
        time.sleep(0.5)

    def Bristles_Realy_Power_Off(self):
        GPIO.output(Bristles_Realy, GPIO.LOW)
        print("Bristles_Realy_Power_Off")
        time.sleep(0.5)

    def Bristles_Up(self):
        Bristles_Top = GPIO.input(Bristles_Top_LS)
        GPIO.output(DIR, 1)
        if(Bristles_Top == False):
            for x in range(20):
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)
                print("Bristles_Up")
        else:
            print("Bristles_To_The_Top")

    def Bristles_Down(self):
        Bristles_Bottom = GPIO.input(Bristles_Bottom_LS)
        GPIO.output(DIR, 0)
        if(Bristles_Bottom == True):
            for x in range(20):
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)
                print("Bristles_Down")
        else:
            print("Bristles_To_The_Bottom")

    def Automatically_Open(self):
        self.Conveyor_Realy_Power_On()
        self.Bristles_Realy_Power_On()
        print("All Open")

    def Automatically_Close(self):
        self.Conveyor_Realy_Power_Off()
        self.Bristles_Realy_Power_Off()
        print("All Off")

    def Bristles_Auto_On(self):
        print("Bristles_Auto_On")
        self.pushButton_5.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.Thread_3.singal_2.connect(self.open_2)
        self.Thread_3.start()

    def Bristles_Auto_Off(self):
        print("Bristles_Auto_Off")
        self.Thread_3.is_off = False
        self.open_2()

    def open_2(self):
        self.pushButton_5.setEnabled(True)
        self.pushButton_6.setEnabled(True)
    
    def show_camera(self):
        flag,self.image = self.cap.read()
        show = cv2.resize(self.image,(widthImg,heightImg))

        
        # show = show[y:y+h, x:x+w]

        # imgGray = cv2.cvtColor(show, cv2.COLOR_BGR2GRAY) 
        # imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
        # # retval, thresholded = cv2.threshold(imgBlur, 125, 255, cv2.THRESH_BINARY_INV)
        # # #  + cv2.THRESH_OTSU
        # # kernel = np.ones((9,9))
        # # imgDial = cv2.dilate(thresholded, kernel, iterations = 1)
        # # imgProcessing = cv2.erode(imgDial, kernel, iterations = 1)
        # canny = cv2.Canny(imgBlur, 30, 150)
        # contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # for contour in contours:
        #     Area = cv2.contourArea(contour)
        #     if 3000 > Area > 850:
        #         cv2.drawContours(show, contour, -1, (255, 255, 255), 2)

        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB) 


        showImage = QImage(show.data, show.shape[1],show.shape[0],QImage.Format_RGB888)
        self.label_10.setPixmap(QPixmap.fromImage(showImage))



class Thread_1(QThread): #香菇梗推出機構
    singal = pyqtSignal()
    def __init__(self):
        super(Thread_1, self).__init__()
        self.Pusher_input_BOTTOM = GPIO.input(16)
        self.Pusher_input_TOP = GPIO.input(23)
    def run(self):
        GPIO.output(Motor_Reverse_Realy, GPIO.LOW)
        GPIO.output(Motor_Forward_Realy, GPIO.LOW)
        self.Pusher_input_BOTTOM = GPIO.input(16)
        while self.Pusher_input_BOTTOM == True:
            self.Pusher_input_BOTTOM = GPIO.input(16)
            GPIO.output(Motor_Reverse_Realy, GPIO.HIGH)
            time.sleep(0.01)
        print("STOP")
        GPIO.output(Motor_Reverse_Realy, GPIO.LOW)
        self.Pusher_input_TOP = GPIO.input(23)
        time.sleep(0.5)
        for a in range(10):
            GPIO.output(Motor_Forward_Realy, GPIO.HIGH)
            print("Motor_Forward")
            time.sleep(1)
        print("STOP1")
        GPIO.output(Motor_Forward_Realy, GPIO.LOW)
        self.singal.emit()
        time.sleep(1)
        
        

class Thread_2(QtCore.QThread): #香菇檢測
    avgArea = QtCore.pyqtSignal(float)
    avgLength = QtCore.pyqtSignal(int)
    avgEffect = QtCore.pyqtSignal(float)
    def __init__(self, argument_):
        super(Thread_2, self).__init__()
        self.cap = argument_
        widthImg = 512
        heightImg = 384
        x = 0
        y = 50
        w = 500
        h = 100
    def run(self):
        while True:
            try:
                time.sleep(0.1)
                success, img = self.cap.read()
                img = cv2.resize(img,(widthImg,heightImg))
                imgProcessing = self.preProcessing(img)
                self.getContours(imgProcessing)
                self.avgArea.emit(self.area)
                self.avgLength.emit(self.length)
                self.avgEffect.emit(self.effect)        
            except:
                pass
    def preProcessing(self, img):
        img = img[y:y+h, x:x+w]
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
        imgProcessing = cv2.Canny(imgBlur, 30, 150)
        # retval, thresholded = cv2.threshold(imgBlur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # kernel = np.ones((5,5))
        # imgDial = cv2.dilate(thresholded, kernel, iterations = 1)
        # imgProcessing = cv2.erode(imgDial, kernel, iterations = 1)
        return imgProcessing
    def getContours(self, img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        csv_path = os.path.join("Data", "SHIITAKE_DATA.csv")
        self.effect = 0
        for contour in contours:
            Area = cv2.contourArea(contour)
            if 3000 > Area > 850 :
                self.effect = self.effect + 1 
                feature_list = []
                M = cv2.moments(contour)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x,y,w,h=cv2.boundingRect(contour)
                self.area = cv2.contourArea(contour) / 20
                self.length = cv2.arcLength(contour, True) / 4.75
                x_long = abs(x-cx)
                y_long = abs(y-cx)
                w_long = abs(w-cx)
                h_long = abs(h-cx)
                # try:
                #     feature_list.append(self.area)
                #     feature_list.append(self.length)
                #     feature_list.append(x_long)
                #     feature_list.append(y_long)
                #     feature_list.append(w_long)
                #     feature_list.append(h_long)
                #     with open(csv_path, 'a', newline='') as files:
                #         writer = csv.writer(files)
                #         writer.writerow(feature_list)
                #         print("OK")
                # except:
                #     pass
        try:
            return self.area, self.length, self.effect
        except:
            pass
 
class Thread_3(QThread): #自動模式
    singal_2 = pyqtSignal()
    def __init__(self, argument_):
        super(Thread_3, self).__init__()
        widthImg = 512
        heightImg = 384
        x = 0
        y = 50
        w = 500
        h = 100
        self.cap = argument_
        self.Bristles_Top_LS = 17
        self.Bristles_Bottom_LS = 4
        self.DIR = 18
        self.STEP = 24
        self.Number = 2
        self.up = 0.5
        self.down = 0.5
        self.is_off = 1
    def run(self):
        self.zero()
        self.origin()
        while self.is_off:
            time.sleep(2)
            try:
                success, img = self.cap.read()
                imgProcessing = self.preProcessing(img)
                self.area, self.length, self.effect = self.getContours(imgProcessing, self.Number)
            # self.avgArea.emit(self.area)
            # self.avgLength.emit(self.length)
            # self.avgEffect.emit(self.effect)
            except:
                pass
            if self.effect <= 1:
                self.Number, self.state = self.get_action()
                self.action(self.Number, self.state)
            else:
                pass
            
        print("ok")
        self.singal_2.emit()
    def zero(self):
        Bristles_Bottom = GPIO.input(self.Bristles_Bottom_LS)
        while (Bristles_Bottom == True):
            Bristles_Bottom = GPIO.input(self.Bristles_Bottom_LS)
            GPIO.output(self.DIR, 0)
            for x in range(5):
                GPIO.output(self.STEP, GPIO.HIGH)
                sleep(0.005)
                GPIO.output(self.STEP, GPIO.LOW)
                sleep(0.005)
        print("ZERO OK")
    def origin(self):
        for number_turn in range(self.Number):
            GPIO.output(self.DIR, 1)
            for x in range(500):
                GPIO.output(self.STEP, GPIO.HIGH)
                sleep(0.01)
                GPIO.output(self.STEP, GPIO.LOW)
                sleep(0.01)
        print("Number_Zero")
        self.Number = 0
        return self.Number
    def get_action(self):
        direction = ["up", "down"]
        next_direction = np.random.choice(direction, p = [self.up, self.down])
        if self.Number >= 200:
            self.Number = self.Number - 20
            self.state = 0
            print("down")
        elif self.Number <= -200:
            self.Number = self.Number + 20
            self.state = 1
            print("up")
        else:
            if next_direction == "up":
                self.Number = self.Number + 20
                self.state = 1
                print("up")
            elif next_direction == "down":
                self.Number = self.Number - 20
                self.state = 0
                print("down")
        return self.Number, self.state
    def action(self, number, state):
        GPIO.output(self.DIR, state)
        for x in range(20):
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(0.01)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(0.01)           
        print(number)
    def preProcessing(self, img):
        img = cv2.resize(img,(widthImg,heightImg))
        img = img[y:y+h, x:x+w]
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
        imgProcessing = cv2.Canny(imgBlur, 30, 150)
        return imgProcessing
    def getContours(self, img, number):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        csv_path = os.path.join("Data", "SHIITAKE_DATA.csv")
        self.effect = 0
        for contour in contours:
            Area = cv2.contourArea(contour)
            if 3000 > Area > 900:
                self.effect = self.effect + 1
                feature_list = []
                M = cv2.moments(contour)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x,y,w,h=cv2.boundingRect(contour)
                self.area = cv2.contourArea(contour)
                self.length = cv2.arcLength(contour, True)
                x_long = abs(x-cx)
                y_long = abs(y-cx)
                w_long = abs(w-cx)
                h_long = abs(h-cx)
                
                try:
                    feature_list.append(self.area)
                    feature_list.append(self.length)
                    feature_list.append(x_long)
                    feature_list.append(y_long)
                    feature_list.append(w_long)
                    feature_list.append(h_long)
                    feature_list.append(number)
                    with open(csv_path, 'a', newline='') as files:
                        writer = csv.writer(files)
                        writer.writerow(feature_list)
                        print("OK")
                except:
                    pass
        try:
            return self.area, self.length, self.effect
        except:
            pass

def exit():
    GPIO.output(Conveyor_Realy, GPIO.LOW)
    GPIO.output(Bristles_Realy, GPIO.LOW)
    GPIO.output(Motor_Reverse_Realy, GPIO.LOW)
    GPIO.output(Motor_Forward_Realy, GPIO.LOW)
    print("EXIT")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = PyMainWindow()
    ui.show()
    atexit.register(exit)
    sys.exit(app.exec_())
    