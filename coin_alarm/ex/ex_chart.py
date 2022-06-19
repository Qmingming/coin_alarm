import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("window.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.graph_verticalLayout.addWidget(self.canvas)
        x = np.arange(0, 100, 1)
        y = np.sin(x)

        ax = self.fig.add_subplot(111)
        ax.plot(x, y, label="sin")
        ax.set_xlabel("x")
        ax.set_xlabel("y")

        ax.set_title("my sin graph")
        ax.legend()

        x = np.arange(0, 100, 1)
        y = np.cos(x)
        ax.plot(x, y, label="cos")

        self.canvas.draw()

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

