#!/usr/bin/python
# coding: utf-8
from test import Ui_CamShow
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog
from PyQt5.QtCore import QTimer,QCoreApplication
from PyQt5.QtGui import QPixmap
import cv2
import qimage2ndarray
import time
import pyqtgraph as py
import numpy as np
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import Qt,QRect

class CamShow(QMainWindow,Ui_CamShow):
    def __init__(self,parent=None):
        super(CamShow,self).__init__(parent)
        self.setupUi(self)
        self.PrepWidgets()
        self.not_open = 0 #flag
        self.PrepParameters()
        self.Timer = QTimer(self)    
        self.CallBackFunctions()
        self._num = 0
        self.getSave_arr = []
        self.getPixel_arr = []     
        self.Timer.timeout.connect(self.TimerOutFun)       
        self.stopbt = 0
        #self.draw.plotItem.showGrid(True, True, 0.7)
        

    #控件初始化
    def PrepWidgets(self):
        self.PrepCamera()
        self.StopBt.setEnabled(False)
        self.RecordBt.setEnabled(False)
        self.Exposure.setEnabled(False)
        self.Btn_Log.setEnabled(False)
        f = open('pixel_read.txt','r')
        f1 = open("wave_read.txt",'r')
        lines = f.readlines()
        lines1 = f1.readlines()
        i = 0
        for line in lines:
            _spl = line.split('\n')
            if i == 0:
                self.P1.setText(_spl[0])
            elif i == 1:
                self.P2.setText(_spl[0])
            elif i == 2:
                self.P3.setText(_spl[0])
            elif i == 3:
                self.P4.setText(_spl[0])
            elif i == 4:
                self.P5.setText(_spl[0])
            elif i == 5:
                self.P6.setText(_spl[0])
            elif i == 6:
                self.P7.setText(_spl[0])
            elif i == 7:
                self.P8.setText(_spl[0])
            
            i+=1

        i = 0
        for line in lines1:
            _spl = line.split('\n')
            if i == 0:
                self.W1.setText(_spl[0])
            elif i == 1:
                self.W2.setText(_spl[0])
            elif i == 2:
                self.W3.setText(_spl[0])
            elif i == 3:
                self.W4.setText(_spl[0])
            elif i == 4:
                self.W5.setText(_spl[0])
            elif i == 5:
                self.W6.setText(_spl[0])
            elif i == 6:
                self.W7.setText(_spl[0])
            elif i == 7:
                self.W8.setText(_spl[0])
            
            i+=1
            
        f.close()
        f1.close()


    def PrepCamera(self):
        self.camera=cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,1920)
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25)
        #self.camera.set(cv2.CAP_PROP_EXPOSURE,float(0.1))
        #self.camera.set(cv2.CAP_PROP_ISO_SPEED,100)
  

    def PrepParameters(self):
        self.RecordFlag=0  # 0=not save video, 1=save
        self.RecordPath='D:/Python/PyQt/'
        self.FilePathLE.setText(self.RecordPath)
        self.Image_num=0 # 讀取圖片的次數
        self.Exposure.currentIndexChanged.connect(lambda:self.camera.get(15))
        self.SetExposure()

        

    def CallBackFunctions(self):
        self.FilePathBt.clicked.connect(self.SetFilePath)
        self.ShowBt.clicked.connect(self.StartCamera)
        self.StopBt.clicked.connect(self.StopCamera)
        self.RecordBt.clicked.connect(self.RecordCamera)
        self.ExitBt.clicked.connect(self.ExitApp)
        self.Timer.timeout.connect(self.TimerOutFun)
        self.BtnGo.clicked.connect(self.calculate)
        self.Exposure.activated.connect(self.SetExposure)
        self.Btn_Log.clicked.connect(self.saveLog)

    def SetExposure(self):
        exposure_time = float(self.Exposure.currentText())
        print(exposure_time)
        self.camera.set(15,exposure_time)

          

    def StartCamera(self):
        self.ShowBt.setEnabled(False)
        self.StopBt.setEnabled(True)
        self.RecordBt.setEnabled(True)
        self.Exposure.setEnabled(True)
        self.GrayCheck.setEnabled(True)
        self.RecordBt.setText('Record')
        self.Timer.start(1)
        self.timelb=time.clock()
    

    def StopCamera(self):
        if self.StopBt.text() == 'Stop':
            self.StopBt.setText('Continue')
            #self.stopbt = 0
            self.RecordBt.setText('Save Pic')
            self.Timer.stop()
            self.Btn_Log.setEnabled(True)
        else:
            self.StopBt.setText('Stop')
            #self.stopbt = 1
            self.RecordBt.setText('Record')
            self.Timer.start(1)
            self.Btn_Log.setEnabled(False)


    def TimerOutFun(self):
        self.not_open
        success,self.img=self.camera.read()

        if self.GrayCheck.isChecked():
            self.GrayImg = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        if success:
            
            self.DispImg()           
            self.CopyImg()            
            self.drawAvg()                         
            self.Image_num+=1 #讀取圖片的次數
            
            if self.not_open != 0:
                self.drawAvg_after_calculate()
                       
            if self.RecordFlag:
                if self.GrayCheck.isChecked():
                    color = cv2.cvtColor(self.GrayImg, cv2.COLOR_GRAY2RGB) #再轉換一次灰階到彩色才會有三通到，儲存影片才能成功
                    self.video_writer.write(color)
                else:
                    self.video_writer.write(self.img)
                        
            if self.Image_num%10==9:
               # frame_rate = 10/(time.clock()-self.timelb)
               # self.FpsLCD.display(frame_rate)
               # self.timelb=time.clock()
                self.FpsLCD.display(self.camera.get(5))
                self.WidthLCD.display(self.camera.get(3))
                self.HeightLCD.display(self.camera.get(4))
                   
    
    def DispImg(self):
        self.GrayImg = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        #图像调整为490像素，算出新宽度與舊宽度的比值r，然后用比值r乘以舊高度，得到新高度。
        r = 490.0/self.img.shape[1]
        dim = (490, int(self.img.shape[0]*r))
        self.resized = cv2.resize(self.img, dim, interpolation=cv2.INTER_AREA)
        self.Gray_resized = cv2.resize(self.GrayImg, dim, interpolation=cv2.INTER_AREA)

        if self.GrayCheck.isChecked():
            #qimg = qimage2ndarray.array2qimage(self.GrayImg)
            qimg = qimage2ndarray.array2qimage(self.Gray_resized)
           
        else:
            #CVimg = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            CVimg = cv2.cvtColor(self.resized, cv2.COLOR_BGR2RGB)       
            qimg = qimage2ndarray.array2qimage(CVimg)
        
        self.DispLb.setPixmap(QPixmap(qimg))
        self.DispLb.show()


    def CopyImg(self):
        #ret=QRect(10,260,501,20) # QRect ( int left, int top, int width, int height )
        r = 490/2560
        r2 = 1920 * r
        #X = int(self.roi_X.text())
        X2 = int(self.roi_X.text()) * r
        #Y = int(self.roi_Y.text())
        Y2 = int(self.roi_Y.text()) * r2
        W = 2560-X
        #W = int(self.roi_Width.text())
        H = int(self.roi_Height.text())
        #ret = QRect(X,Y,W,H)
        ret = QRect(X2,Y2,W,H)

        if self.GrayCheck.isChecked():
            #qimg = qimage2ndarray.array2qimage(self.GrayImg)
            qimg = qimage2ndarray.array2qimage(self.Gray_resized)
            
        else:
            #CVimg = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB) 
            CVimg = cv2.cvtColor(self.resized,cv2.COLOR_BGR2RGB)       
            qimg = qimage2ndarray.array2qimage(CVimg)

        b=qimg.copy(ret)
        self.DispCopyImg.setPixmap(QPixmap(b))
        self.DispCopyImg.show()

    
    def SetFilePath(self):
        dirname = QFileDialog.getExistingDirectory(self, "瀏覽", '.')
        if dirname:

            self.FilePathLE.setText(dirname)
            self.RecordPath=dirname+'/'

    def RecordCamera(self):
        tag = self.RecordBt.text()
        if tag == 'Save Pic':
            image_name=self.RecordPath+'self.image'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.jpg'
            print(image_name)
            if self.GrayCheck.isChecked():
                cv2.imwrite(image_name,self.CVimg)
            else:
                cv2.imwrite(image_name,self.img)

            
        elif tag =='Record2':
            self.RecordBt.setText('Stop')
            video_name = self.RecordPath + 'video' + time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())) + '.avi'
            if self.GrayCheck.isChecked():
                size = (self.GrayImg.shape[1],self.GrayImg.shape[0])
            else:
                size = (self.img.shape[1],self.img.shape[0])          
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            self.video_writer = cv2.VideoWriter(video_name, fourcc , self.camera.get(5), size)
            self.RecordFlag=1
            self.StopBt.setEnabled(False)
            self.ExitBt.setEnabled(False)
        
        elif tag == 'Record':
           # for i in range(1,10):
            print(self.img)

        elif tag == 'Stop':
            self.RecordBt.setText('Record')
            self.video_writer.release()
            self.RecordFlag = 0
            self.StopBt.setEnabled(True)
            self.ExitBt.setEnabled(True)


    def drawAvg(self):
        self.draw_2.clear()
     
        img2RGB = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img2RGB,cv2.COLOR_RGB2GRAY)
        
        #初始化numpy arr
        r_arr = np.zeros((2560,1) , np.uint8)
        g_arr = np.zeros((2560,1) , np.uint8)
        b_arr = np.zeros((2560,1) , np.uint8)
        Gray_arr = np.zeros((2560,1),np.uint8)

        r_arr[:,0] = np.sum(img2RGB[int(self.roi_Y.text()):int(int(self.roi_Y.text())+ int(self.roi_Height.text())),:,0],0) / int(self.roi_Height.text())
        g_arr[:,0] = np.sum(img2RGB[int(self.roi_Y.text()):int(int(self.roi_Y.text())+ int(self.roi_Height.text())),:,1],0) / int(self.roi_Height.text())
        b_arr[:,0] = np.sum(img2RGB[int(self.roi_Y.text()):int(int(self.roi_Y.text())+ int(self.roi_Height.text())),:,2],0) / int(self.roi_Height.text())
        Gray_arr[:,0] = np.sum(gray[int(self.roi_Y.text()):int(int(self.roi_Y.text())+ int(self.roi_Height.text())), : ],0 )/ int(self.roi_Height.text())
        
        self.SavePixel_arr = np.zeros((2560,2),dtype=np.int)  # SavePixel_arr 存Gray_arr
        _index = [i for i in range(2560)]
        self.SavePixel_arr[:,0] = np.array(_index)
        self.SavePixel_arr[:,1] = Gray_arr[:,0]

        
        self.avg = int(self.Avg_logout.text()) #user輸入平均次數
        
        # 如果 getPixel_arr的長度大於10，就把第一筆資料刪除，固定只存10筆資料
        if len(self.getPixel_arr) >= self.avg:
            self.getPixel_arr.pop(0)
        self.getPixel_arr.append(self.SavePixel_arr)
            
    

        x = np.linspace(0,2560,2560)
        self.draw_2.setRange(xRange=[0,2560]) # 固定x軸 不會拉動
        self.draw_2.setRange(yRange=[0,255]) # 固定y軸 不會拉動
   
        self.draw_2.plot(x, r_arr[:,0] , pen='r')
        self.draw_2.plot(x, g_arr[:,0] , pen='g')
        self.draw_2.plot(x, b_arr[:,0] , pen='b')
        self.draw_2.plot(x,Gray_arr[:,0],pen='w')

        if self.GrayCheck.isChecked():
            self.draw_2.clear()
            self.draw_2.plot(x,Gray_arr[:,0],pen='w')


    def calculate(self):
        self.not_open += 1
        pixel_array = []
        wave_array = []

        

        
        
        if self.P1.text():
            #a1 = float(text[0])
            a1 = float(self.P1.text())
            pixel_array.append(a1)
            #print("a1=",a1)
            if self.W1.text():
                b1 = float(self.W1.text())
                wave_array.append(b1)
                #print("b1=",b1)

        if self.P2.text():
            #a2 = float(text[1])
            a2 = float(self.P2.text())
            pixel_array.append(a2)           
            if self.W2.text():
                b2 = float(self.W2.text())
                wave_array.append(b2)

        if self.P3.text():
            a3 = float(self.P3.text())
            pixel_array.append(a3)
            if self.W3.text():
                b3 = float(self.W3.text())
                wave_array.append(b3)

        if self.P4.text():
            a4 = float(self.P4.text())
            pixel_array.append(a4)
            if self.W4.text():
                b4 = float(self.W4.text())
                wave_array.append(b4)

        if self.P5.text():
             a5 = float(self.P5.text())
             pixel_array.append(a5)
             if self.W5.text():
                 b5 = float(self.W5.text())
                 wave_array.append(b5)

        if self.P6.text():
             a6 = float(self.P6.text())
             pixel_array.append(a6)
             if self.W6.text():
                 b6 = float(self.W6.text())
                 wave_array.append(b6)

        if self.P7.text():
             a7 = float(self.P7.text())
             pixel_array.append(a7)
             if self.W7.text():
                 b7 = float(self.W7.text())
                 wave_array.append(b7)
            
        if self.P8.text():
             a8 = float(self.P8.text())
             pixel_array.append(a8)
             if self.W8.text():
                 b8 = float(self.W8.text())
                 wave_array.append(b8)
        
        if self.P9.text():
             a9 = float(self.P9.text())
             pixel_array.append(a9)
             if self.W9.text():
                 b9 = float(self.W9.text())
                 wave_array.append(b9)
        
        if self.P10.text():
             a10 = float(self.P10.text())
             pixel_array.append(a10)
             if self.W10.text():
                 b10 = float(self.W9.text())
                 wave_array.append(b10)
   
        x = pixel_array
        y = wave_array
        print(x)
        print(y)
        num = int(self.comboBox.currentText()) #冪次
        parameter = np.polyfit(x,y,num)
        print(parameter)
        print(parameter[0])
        print(parameter[1])
        line = np.poly1d(parameter)
        print(line)
        
        #self.a0 = parameter[1]
        #self.a1 = parameter[0]
        if num == 1:    
            result = "a1係數:"+ str(parameter[0]) + "\n" + "a0係數:"+ str(parameter[1]) +"\n"+ "y=" + str(line) 
            self.results_window.setText(result)
            self.graphicsView.clear()
            self.graphicsView.plot(x,y,pen='g')
            self.p0 = parameter[0]
            self.p1 = parameter[1]

        if num == 2:
            result = "a2係數:"+ str(parameter[0]) + "\n" + "a1係數:"+ str(parameter[1]) + "\n" + "a0係數:"+ str(parameter[2])  + "\n"+ "y=" + str(line)   
            self.results_window.setText(result)
            self.graphicsView.clear()
            self.graphicsView.plot(x,y,pen='g')
            self.p0 = parameter[0]
            self.p1 = parameter[1]
            self.p2 = parameter[2]



        if num == 3: 
            result = "a3係數:"+ str(parameter[0]) + "\n" +"a2係數:"+ str(parameter[1]) + "\n" + "a1係數:"+ str(parameter[2]) + "\n" + "a0係數:"+ str(parameter[3]) +"\n"+ "y=" + str(line)   
            self.results_window.setText(result)
            self.graphicsView.clear()
            self.graphicsView.plot(x,y,pen='g')
            self.p0 = parameter[0]
            self.p1 = parameter[1]
            self.p2 = parameter[2]
            self.p3 = parameter[3]

        if num == 4: 
            result = "a4係數:"+ str(parameter[0]) + "\n" +"a3係數:"+ str(parameter[1]) + "\n" + "a2係數:"+ str(parameter[2]) + "\n" + "a1係數:"+ str(parameter[3]) +"\n"+ "a0係數:"+ str(parameter[4]) + "\n"+ "y=" + str(line)   
            self.results_window.setText(result)
            self.graphicsView.clear()
            self.graphicsView.plot(x,y,pen='g')
            self.p0 = parameter[0]
            self.p1 = parameter[1]
            self.p2 = parameter[2]
            self.p3 = parameter[3]
            self.p4 = parameter[4]

        if num == 5: 
            result = "a5係數:"+ str(parameter[0]) + "\n" +"a4係數:"+ str(parameter[1]) + "\n" + "a3係數:"+ str(parameter[2]) + "\n" + "a2係數:"+ str(parameter[3]) +"\n"+ "a1係數:"+ str(parameter[4]) + "\n"+ "a0係數:"+ str(parameter[5]) +  "\n" + "y=" + str(line)   
            self.results_window.setText(result)
            self.graphicsView.clear()
            self.graphicsView.plot(x,y,pen='g')
            self.p0 = parameter[0]
            self.p1 = parameter[1]
            self.p2 = parameter[2]
            self.p3 = parameter[3]
            self.p4 = parameter[4]
            self.p5 = parameter[5]
    


    def drawAvg_after_calculate(self):
        self.draw_3.clear()
        img2RGB = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img2RGB,cv2.COLOR_RGB2GRAY)
        
        #初始化numpy arr   
        Gray_arr = np.zeros((2560,1),np.uint8)

        Gray_arr[:,0] = np.sum(gray[int(self.roi_Y.text()):int(int(self.roi_Y.text())+ int(self.roi_Height.text())), : ],0 )/ int(self.roi_Height.text())
        #for i in range(640):   
            #Gray_arr[i,0] = np.sum(gray[260:280 , i ])/ int(self.roi_Height.text())
            #print(Gray_arr)

        #x_0 = self.a0 * 0 + self.a1
        #x_640 =self.a0 * 640 + self.a1
        #_x = np.linspace(x_0,x_640,640)

        num = int(self.comboBox.currentText())
        if num == 1:
            x_0 = self.p0 * 0 + self.p1
            x_2560 =self.p0 * 2560 + self.p1
            _x = np.linspace(x_0,x_2560,2560)
            #print( self.p0,self.p1,x_0)
            #print(self.p0,self.p1,x_640)

        if num == 2:
            #x_0 = self.p0 * 0 + self.p1 *0 + self.p2
            x_0 = math.pow(0,2)* self.p0 + self.p1 * 0 + self.p2
            #x_640 =self.p0 * 640 + self.p1 *640 + self.p2
            x_640 = math.pow(2560,2) * self.p0 + self.p1 * 2560 + self.p2
            _x = np.linspace(x_0,x_2560,2560)
            #print( self.p0,self.p1,self.p2,x_0)
            #print(self.p0,self.p1,self.p2,x_640)

        if num == 3:
            #x_0 = self.p0 * 0 + self.p1 *0 + self.p2 *0 + self.p3
            x_0 = math.pow(0,3)* self.p0 + math.pow(0,2)*self.p1 + math.pow(0,1)*self.p2 + self.p3
            #x_640 =self.p0 * 640 + self.p1 *640 + self.p2 *640 + self.p3
            x_2560 = math.pow(2560,3)* self.p0 + math.pow(2560,2)*self.p1 + math.pow(2560,1)*self.p2 + self.p3
            _x = np.linspace(x_0,x_2560,2560)

        if num == 4:
            #x_0 = self.p0 * 0 + self.p1 *0 + self.p2 *0 + self.p3 *0 + self.p4
            x_0 = math.pow(0,4)* self.p0 + math.pow(0,3)*self.p1 + math.pow(0,2)*self.p2 + math.pow(0,1)*self.p3 + self.p4
            #x_640 =self.p0 * 640 + self.p1 *640 + self.p2 *640 + self.p3 *640 + self.p4
            x_2560 = math.pow(2560,4)* self.p0 + math.pow(2560,3)*self.p1 + math.pow(2560,2)*self.p2 + math.pow(640,1)*self.p3 + self.p4
            _x = np.linspace(x_0,x_2560,2560)

        if num == 5:
            #x_0 = self.p0 * 0 + self.p1 *0 + self.p2 *0 + self.p3 *0 + self.p4 *0 + self.p5
            x_0 = math.pow(0,5)* self.p0 + math.pow(0,4)*self.p1 + math.pow(0,3)*self.p2 + math.pow(0,2)*self.p3 + math.pow(0,1)*self.p4 + self.p5
            #x_640 =self.p0 * 640 + self.p1 *640 + self.p2 *640 + self.p3 *640 + self.p4 *640 + self.p5
            x_2560 = math.pow(2560,5)* self.p0 + math.pow(2560,4)*self.p1 + math.pow(2560,3)*self.p2 + math.pow(2560,2)*self.p3 + math.pow(2560,1)*self.p4 + self.p5
            _x = np.linspace(x_0,x_2560,2560)
     

        self.save_arr = np.zeros((2560,2),dtype=np.uint32)  # save_arr存Gray_arr
        
        
        
        for i in range(640): 
            #self.save_arr[i,0] = (x_640 - x_0) / 640 * (i + 1)
            self.save_arr[i,1] = Gray_arr[i,0]
            if num == 1:
                self.save_arr[i,0] = self.p0 * i + self.p1
            if num == 2:
                self.save_arr[i,0] =math.pow(i,2) * self.p0 + self.p1 * i + self.p2

        self.avg = int(self.Avg_logout.text()) #user輸入平均次數
        
        # 如果 getSave_arr的長度大於10，就把第一筆資料刪除，固定只存10筆資料
        if len(self.getSave_arr) >= self.avg:
            self.getSave_arr.pop(0)
        self.getSave_arr.append(self.save_arr)
        
        #print(self.avg)
            

        
        self.y_arr = np.zeros((2560,1),dtype=np.float16)  #y_arr = [] #存 getSave_arr相加的值
        for arr in self.getSave_arr:
            for i in range(2560):
                self.y_arr[i,0] = np.add(self.y_arr[i,0], arr[i,1])
            

        self.Gray_arr = np.zeros((2560,1),dtype=np.float16)  
        for i in range(2560):
            self.Gray_arr[i,0] = self.y_arr[i,0]/ self.avg
        
        
        self.draw_3.setRange(xRange=[0,x_2560]) # 固定x軸 不會拉動
        self.draw_3.setRange(yRange=[np.amin(Gray_arr),np.amax(Gray_arr)]) # 固定y軸 不會拉動    
        self.draw_3.plot(_x,self.Gray_arr[:,0],pen='w')
        
    
    
    def saveLog(self):
        fp = open('wavelength.txt' , 'w')
        fp2 = open('pixel.txt','w')
        # for i in range(640):
        #     fp.writelines(str(self.save_arr[i,0]) + ',' + str(self.save_arr[i,1]) + '\n')
       

        # 以下: 存波長對強度 
        self.y_arr = np.zeros((2560,1),dtype=np.float16)  #y_arr = [] #存 getSave_arr相加的值
        for arr in self.getSave_arr:
            for i in range(2560):
                self.y_arr[i,0] = np.add(self.y_arr[i,0], arr[i,1])
                #fp.writelines(str(self.save_arr[i,0]) + ','+ str(arr[i,1]) + '\n') #存顯示(self.avg)筆資料
            
        for i in range(2560):
            fp.writelines(str(self.save_arr[i,0]) + ','+ str(self.y_arr[i,0]/self.avg) + '\n')
        
        # 以下:存pixcel對強度
        self.add_arr = np.zeros((2560,1),dtype=np.float16)
        for arr2 in self.getPixel_arr:
            for ii in range(2560):
                self.add_arr[ii,0] = np.add(self.add_arr[ii,0], arr2[ii,1])

        for ii in range(2560):
            fp2.writelines(str(self.SavePixel_arr[ii,0]) + ',' + str(self.add_arr[ii,0]/self.avg) + '\n')
            
            
            
   
          
        fp.close()
        print('saving done!')
    
       
    def ExitApp(self):
        self.Timer.Stop()
        self.camera.release()
        QCoreApplication.quit()
        
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui=CamShow()
    ui.show()
    app.exec_()
    print(self.StopBt.setText())
