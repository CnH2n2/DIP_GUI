import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

# 导入designer工具生成的MainWindow模块
from MainWindow import Ui_MainWindow
from ImageProcessing import DIP

import cv2 as cv


class MyMainForm(QMainWindow, Ui_MainWindow,DIP):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        # 创建对象实例
        self.dip=DIP()
        # 储存用户的历史操作
        self.historyAction = []
        # 当前编辑的图片
        self.captured=[]
        self.current_img=[]
        # 当前操作状态
        self.currentState=[]

        # 隐藏控件
        self.horizontalSlider.setHidden(True)
        self.doubleSpinBox.setHidden(True)

        # 添加槽函数

        # 打开图片文件
        self.actionOpen.triggered.connect(lambda: self.displayAction("打开图片"))
        self.actionOpen.triggered.connect(self.openFile)

        # 添加高斯噪声
        self.actionGauss_noise.triggered.connect(lambda: self.displayAction("添加高斯噪声"))
        self.actionGauss_noise.triggered.connect(lambda: self.addNoise(NoiseType="Gauss"))
        self.actionGauss_noise.triggered.connect(self.showWidgets)

        # 添加椒盐噪声
        self.actionPepper_noise.triggered.connect(lambda: self.displayAction("添加椒盐噪声"))
        self.actionPepper_noise.triggered.connect(lambda: self.addNoise(NoiseType="Pepper"))
        self.actionPepper_noise.triggered.connect(self.showWidgets)

        # 图像模糊
        self.actionBlur.triggered.connect(lambda: self.displayAction("图像模糊"))
        self.actionBlur.triggered.connect(self.blurAction)
        self.actionBlur.triggered.connect(self.showWidgets)


        self.actionHist.triggered.connect(lambda:self.displayAction('直方图增强'))
        self.actionHist.triggered.connect(self.Hist)

        self.actionLog.triggered.connect(lambda:self.displayAction('对数变换'))
        self.actionLog.triggered.connect(self.Log)
        self.actionLog.triggered.connect(self.showWidgets)

        self.action2Gray.triggered.connect(self.ToGray)
        self.action2Gray.triggered.connect(lambda:self.displayAction('图像灰度化'))
        # 恢复原始图像
        self.actionRecover.triggered.connect(lambda:self.DisplayImage(self.captured,self.processing_Image))

        # 参数调整
        self.horizontalSlider.valueChanged.connect(self.paramChange)
        self.doubleSpinBox.valueChanged.connect(self.paramChange)

        # 清除历史菜单
        self.clearButton.pressed.connect(self.clearHistoryMenu)

    # 打开图片并显示
    def openFile(self):
        # 打开文件夹对话框，获取所选文件的路径
        # Tip：filename必须是应为路径，否则·无法用cv.imread打开
        filename, _ = QFileDialog.getOpenFileName(self, "打开")
        if filename:
            # 读取图像文件：
            # 方法1：用openCV读取图像

            # 根据文件路径打开图片
            self.captured = cv.imread(filename)
            self.captured=cv.resize(self.captured,(500,500), interpolation=cv.INTER_AREA)
            # 将BGR图片转换为RGB图片
            self.captured = cv.cvtColor(self.captured, cv.COLOR_BGR2RGB)
            self.DisplayImage(self.captured, self.labelCapture)
            self.current_img=self.captured

    # 在历史菜单栏中显示当前操作
    def displayAction(self, action=""):
        self.historyAction.append(action)
        # 创建字符串列表数据模型实例
        listModel = QStringListModel()
        # 初始化模型的字符串列表内容
        listModel.setStringList(self.historyAction)
        # 在HistoricalOprations_ListView中显示字符串列表
        self.HistoricalOprations_ListView.setModel(listModel)

    # 添加噪声
    def addNoise(self, NoiseType):
        self.currentAction=NoiseType
        # gray_captured = cv.cvtColor(self.captured, cv.COLOR_RGB2GRAY)
        if NoiseType == "Gauss":
            sigma = self.doubleSpinBox.value() / 100.0
            imgNoise = self.dip.addGaussNoise(self.captured, sigma=sigma)

        elif NoiseType == "Pepper":
            SNR = self.doubleSpinBox.value() / 1000.0
            imgNoise = self.dip.addSalt_pepper(self.captured, SNR)
        else:
            print("Error!")
        self.current_img=imgNoise
        self.DisplayImage(imgNoise, self.processing_Image)

    # 图像模糊处理
    def blurAction(self):
        self.currentAction='blur'
        kernel_size=int(self.doubleSpinBox.value()/2)
        if kernel_size==0:
            img_blur=self.current_img
        else:
            img_blur=cv.blur(self.current_img,(kernel_size,kernel_size))
        self.DisplayImage(img_blur,self.processing_Image)


    def Hist(self):
        self.currentAction='hist'
        img_hist=self.dip.hist(self.current_img)
        self.DisplayImage(img_hist,self.processing_Image)

    def Log(self):
        self.currentAction='log'
        img_log=self.dip.log(self.current_img,self.doubleSpinBox.value())
        self.DisplayImage(img_log,self.processing_Image)

    def ToGray(self):
        self.current_img=cv.cvtColor(self.current_img, cv.COLOR_RGB2GRAY)
        # GraphicsView中只能显示RGB三通道格式的图像
        self.current_img=cv.cvtColor(self.current_img,cv.COLOR_GRAY2RGB)
        self.DisplayImage(self.current_img,self.processing_Image)

    # 在GraphicsView中显示图片
    def DisplayImage(self, img, GraphicsView):
        rows, cols, channels = img.shape
        # 计算图片每行的字节数
        bytesPerLine = channels * cols
        # QImage.Format_RGB888:图像以24位RGB格式存储
        QImg = QImage(img.data, cols, rows, bytesPerLine, QImage.Format_RGB888)

        # 将图片从QImage形式转换为QPixmap形式
        pix = QPixmap.fromImage(QImg)
        # 对添加到QGraphicsScene的项目进行实例化
        item = QGraphicsPixmapItem(pix)
        # 对图形视图场景进行实例化
        scene = QGraphicsScene()
        # 为场景添加项目
        scene.addItem(item)
        # 或者也可以直接添加pixmap到场景中
        # scene.addPixmap(pix)

        # 在labelCapture中显示scene
        GraphicsView.setScene(scene)
        # 自适应显示图像
        GraphicsView.fitInView(item)


    # 修改参数
    def paramChange(self):
        self.doubleSpinBox.setValue(self.horizontalSlider.value())
        self.horizontalSlider.setValue(int(self.doubleSpinBox.value()))

        if self.currentAction=='Gauss' or self.currentAction=='Pepper':
            self.addNoise(self.currentAction)
            self.displayAction('修改噪声值')
        elif self.currentAction=='blur':
            self.blurAction()
            self.displayAction('修改模糊参数')
        elif self.currentAction=='log':
            self.Log()
            self.displayAction('修改对数系数')
        else:
            print('Error action!')

    # 显示参数修改控件
    def showWidgets(self):
        self.horizontalSlider.setHidden(False)
        self.doubleSpinBox.setHidden(False)

    # 清除历史菜单
    def clearHistoryMenu(self):
        self.historyAction=[]
        self.displayAction()





if __name__ == "__main__":
    # PyQt5程序都需要QApplication对象
    # sys.argv时命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化，创建MyMainForm对象
    myWin = MyMainForm()
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出
    sys.exit(app.exec())
