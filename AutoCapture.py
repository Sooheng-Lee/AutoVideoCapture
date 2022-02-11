# -*- coding: utf-8 -*-
import sys
import os
import cv2
import struct
import datetime
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar, QLineEdit, QDialog, QSlider, QInputDialog, QTextEdit, QFileDialog, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import QCoreApplication, Qt, QDir
from PyQt5.QtGui import QIntValidator

# Setting Window Class
class SettingWindow(QDialog):
    def __init__(self, frame, savePoint):
        super().__init__()
        self.setFixedSize(350, 150)
        self.setWindowTitle("Setting")
        self.loadDefaultSetting(frame, savePoint)
        self.initUI()
        self.show()
        self.isApply = False
        
    def loadDefaultSetting(self, frame, savePoint):
        self.savePointText = QLineEdit()
        self.savePointText.setText(savePoint)
        self.frameValue = frame
        
    
    def initUI(self):
        settingLayout = QVBoxLayout(self)
        # 캡쳐 파일 저장 포인트 레이아웃
        saveLayout = QHBoxLayout()
        self.savePointText.setReadOnly(True)
        self.savePointText.setFixedSize(310, 20)

        savePointButton = QPushButton("Open")
        savePointButton.setFixedSize(40, 22)
        savePointButton.pressed.connect(self.setSavePoint)
        
        saveLayout.addWidget(self.savePointText)
        saveLayout.addWidget(savePointButton)
        
        # 프레임 설정 레이아웃
        frameLayout = QHBoxLayout()
        #Slider 설정 영역
        self.frameSlider = QSlider(Qt.Horizontal)
        self.frameSlider.setFixedWidth(280)
        self.frameSlider.setRange(1, 100)
        self.frameSlider.setValue(self.frameValue)
        self.frameSlider.valueChanged.connect(self.changeFrameBySlider)
        
        # LineEditor 값 영역
        validator = QIntValidator(1, 100, self)
        self.frameText = QLineEdit()
        self.frameText.setFixedSize(30, 30)
        self.frameText.setText(str(self.frameValue))
        self.frameText.setValidator(validator)
        self.frameText.textChanged.connect(self.changeFrameByEditor)
    
        frameLayout.addWidget(self.frameSlider)
        frameLayout.addWidget(self.frameText)
        settingLayout.addLayout(saveLayout)
        settingLayout.addLayout(frameLayout)
        
        # 설정값 버튼 레이아웃
        buttonsLayout = QHBoxLayout()
        applyButton = QPushButton('Apply')
        applyButton.setFixedWidth(100)
        applyButton.pressed.connect(lambda:self.pressedFinalButton(True))
        cancleButton = QPushButton('Cancle')
        cancleButton.setFixedWidth(100)
        cancleButton.pressed.connect(lambda:self.pressedFinalButton(False))
        buttonsLayout.addWidget(applyButton)
        buttonsLayout.addWidget(cancleButton)
        settingLayout.addLayout(buttonsLayout)
    
    # 슬라이드를 변화시켰을 경우 동작하는 함수
    def changeFrameBySlider(self):
        self.frameValue = self.frameSlider.value()
        self.frameText.setText(str(self.frameSlider.value()))
        
    # LineEditor에 변화가 발생했을 경우 동작하는 함    
    def changeFrameByEditor(self):
        if self.frameText.text()=='':
            self.frameValue = 0
            self.frameSlider.setValue(0)
            self.frameText.setText(str(0))
            return
        self.frameValue = int(self.frameText.text())
        self.frameSlider.setValue(int(self.frameText.text()))
    
    # Save Point를 설정하는 기능
    def setSavePoint(self):
        dirName = QFileDialog.getExistingDirectory(self, 'select Directory', self.savePointText.text())
        if dirName!='':
            self.savePointText.setText(dirName)
    
    # Apply or Cancle을 눌렀을 경우 값을 적용시킬지 결정 후 닫음
    def pressedFinalButton(self, isApply):
        self.isApply = isApply
        self.hide()
        
    def getSavePoint(self):
        return self.savePointText.text()

    def getFrameValue(self):
        return self.frameValue


# Main Widget Class
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 어플리케이션 이름 및 크기 설정
        self.setFixedSize(500, 250)
        self.setWindowTitle("Auto Capture Helper")
        self.initUI()
        self.show()
        self.fileSrcList = []
        
        # 필수 변수 초기설정
        self.readDataFile()
        self.fileCount = 0
        self.isFuncEnable = True
        
    def initUI(self):
        # 버튼 Instance 생성
        self.captureButton = QPushButton('Capture')
        self.captureButton.setAutoRepeat(False)
        self.loadButton = QPushButton('Load')
        self.loadButton.setAutoRepeat(False)
        self.settingButton = QPushButton('Setting')
        self.settingButton.setAutoRepeat(False)
        self.quitButton = QPushButton('Quit')
        self.quitButton.setAutoRepeat(False)
        totalArea = QVBoxLayout()
        # 레이아웃에 버튼 UI 추가 정렬
        buttonArea = QVBoxLayout()
        buttonArea.addWidget(self.captureButton)
        buttonArea.addWidget(self.loadButton)        
        buttonArea.addWidget(self.settingButton)
        buttonArea.addWidget(self.quitButton)
        buttonArea.setSpacing(1)
        
        # ProgressBar 및 File List Layout
        printArea = QVBoxLayout()
        # 파일 목록을 출력할 LineEdit 부분
        self.fileListTable = QTableWidget()
        self.fileListTable.setColumnCount(1)
        self.fileListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fileListTable.setHorizontalHeaderLabels(['File List'])
        
        # progressBar 출력 부분
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setValue(0)
        self.progress.setFormat("{0}%".format(self.progress.value()))
        
        printArea.addWidget(self.fileListTable)
        printArea.addWidget(self.progress)
        printArea.setSpacing(1)
        
        totalArea.addLayout(printArea)
        totalArea.insertSpacing(1, 5)
        totalArea.addLayout(buttonArea)
        self.setLayout(totalArea)
        
        # 버튼 클릭시 이벤트 설정
        self.captureButton.clicked.connect(self.clickCaptureButton)
        self.loadButton.clicked.connect(self.clickLoadButton)
        self.settingButton.clicked.connect(self.clickSettingButton)
        # Quit버튼 클릭 후, 프로그램 종료
        self.quitButton.clicked.connect(QCoreApplication.instance().quit)
    
    #특정키 입력시 발생하는 이벤트 함수    
    def keyPressEvent(self, event):
        # Escape Key 입력시 프로그램 종료
        if event.key() == Qt.Key_Escape:
            self.close()
    
    
    #Capture 버튼 클릭시 사용자가 특정한 프레임의 이미지를 추출
    def clickCaptureButton(self):
        if self.isFuncEnable == False:
            return
        self.setButtonsEnable(False)
        count = 0
        dateTime = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        os.mkdir(self.savePoint + '/' + dateTime)
        for fileSrc in self.fileSrcList:
            video = cv2.VideoCapture(fileSrc)
            while(video.isOpened()):
                ret, image = video.read()
                
                if(int(video.get(1)) % self.frameValue == 0):
                    capturedFileName = fileSrc[len(self.loadPoint) +1:-4]
                    capturedFileName = capturedFileName.replace('/', '_') + '_' + str(self.frameValue)
                    #cv2.imwrite가 한글 경로를 인식하지 못하므로 임의의 이름으로 저장 후 이름변경 과정을 거침
                    tempImageSrc = self.savePoint + '/' + dateTime + '/' + 'tempCaturedSaving' + '.png'
                    imageSrc = self.savePoint + '/' + dateTime + '/' + capturedFileName + '.png'
                    cv2.imwrite(tempImageSrc, image)
                    os.rename(tempImageSrc, imageSrc)
                    count += 1
                    self.progress.setValue(count)
                    self.progress.setFormat("{0}%".format(int(count / self.fileCount * 100)))
                    break
        time.sleep(1)
        self.progress.setValue(0)
        self.progress.setFormat("{0}%".format(0))
        self.setButtonsEnable(True)
                
    #Load 버튼 클릭시 폴더 내부의 자료들 리스트들을 불러옴
    def clickLoadButton(self):
        if self.isFuncEnable == False:
            return
        point = ''
        point = QFileDialog.getExistingDirectory(self, 'select Directory', self.loadPoint)
        if point != '':
            self.loadPoint = point
            self.fileCount = 0
            self.fileSrcList = []
            self.loadFileListInDir(self.loadPoint)
            self.fileListTable.setRowCount(self.fileCount)
            for index in range(self.fileCount):
                self.fileListTable.setItem(index, 0, QTableWidgetItem(self.fileSrcList[index]))
            self.progress.setMaximum(self.fileCount)
            self.writeDataFile()
     
    #특정 디렉토리에 있는 확장명이 일치하는 파일 리스트를 불러옴
    def loadFileListInDir(self, dir):
        if self.isFuncEnable == False:
            return
        fileList = os.listdir(dir)
        for fileName in fileList:
            fileSrc = dir + '/' + fileName
            if os.path.isdir(fileSrc):
                # 하위 디렉토리에 있는 파일 리스트를 가져오기 위해서 재귀함수 사
                self.loadFileListInDir(fileSrc)
            elif os.path.isdir(fileSrc)==False and (fileName.endswith('.mp4') or fileName.endswith('.mov')):
                self.fileSrcList.append(fileSrc)
                self.fileCount += 1
                print(fileSrc)
        
            
    #Setting 버튼 클릭시 Setting 창을 띄우는 메서드
    def clickSettingButton(self):
        if self.isFuncEnable == False:
            return
        self.setButtonsEnable(False)
        self.settingWindow = SettingWindow(self.frameValue, self.savePoint)
        self.settingWindow.exec()
        if self.settingWindow.isApply:
            self.frameValue = self.settingWindow.getFrameValue()
            self.savePoint = self.settingWindow.getSavePoint()
            self.writeDataFile()
        self.setButtonsEnable((True))
        
    
    #설정창이 켜져있거나 Capture중에는 모든 버튼을 사용못하게하 기능을 가진 메서드
    def setButtonsEnable(self, Enabled):
        self.isFuncEnable = Enabled
        self.captureButton.setEnabled(Enabled)
        self.loadButton.setEnabled(Enabled)
        self.settingButton.setEnabled(Enabled)
        self.quitButton.setEnabled(Enabled)
    
        
    #변수에 저장된 값 binary 파일에 저장
    def writeDataFile(self):
        dataFile = open('./setting.dat', 'wt')
        dataFile.write(self.savePoint)
        dataFile.write('\n')
        dataFile.write(self.loadPoint)
        dataFile.write('\n')
        dataFile.write(str(self.frameValue))
        dataFile.close()
    
    #변수에 저장된 값 binary 파일에서 불러오
    def readDataFile(self):
        try:
            dataFile = open('./setting.dat', 'rt')
            self.savePoint = dataFile.readline()
            self.loadPoint = dataFile.readline()
            self.frameValue = dataFile.readline()
            self.savePoint = self.savePoint[:-1]
            self.loadPoint = self.loadPoint[:-1]
            self.frameValue = int(self.frameValue)

        except:
            self.savePoint = './'
            self.loadPoint = './'
            self.frameValue = 1
            self.writeDataFile()
        
            
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    sys.exit(app.exec())