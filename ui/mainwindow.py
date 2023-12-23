from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QMenuBar, QAction, QToolBar, QDockWidget, \
    QListWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui.windowtools import GridGraphicsScene, ZoomableGraphicsView, CustomListWidget
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # 设置窗口的标题
        self.setWindowTitle('AI Studio')

        # 设置主窗口大小略小于屏幕分辨率以避免遮挡任务栏
        self.resize(QDesktopWidget().availableGeometry(self).size() * 0.9)

        # 创建菜单栏
        self.menuBar = self.menuBar()
        fileMenu = self.menuBar.addMenu('&File')
        editMenu = self.menuBar.addMenu('&Edit')
        viewMenu = self.menuBar.addMenu('&View')
        helpMenu = self.menuBar.addMenu('&Help')

        # 添加菜单项和动作
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QApplication.instance().quit)
        fileMenu.addAction(exitAction)

        # 创建工具栏
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        # self.toolbar.addAction(exitAction)

        # 创建侧边栏
        self.toolbox = QDockWidget("Tools", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox)

        toolList = CustomListWidget()
        toolList.setDragEnabled(True)  # 启用拖拽

        # 添加带图标的列表项
        self.addToolItem(toolList, "输入数据", "resources/icons/input_data.png")
        self.addToolItem(toolList, "Preprocessing", "path/to/preprocessing_icon.png")
        self.addToolItem(toolList, "Model", "path/to/model_icon.png")
        self.addToolItem(toolList, "Evaluation", "path/to/evaluation_icon.png")

        self.toolbox.setWidget(toolList)

        # 创建状态栏
        self.statusBar().showMessage('Ready')

        # 创建主操作区域的场景和视图
        self.scene = GridGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setAcceptDrops(True)  # Enable drop acceptance on the view
        self.setCentralWidget(self.view)

        # 显示主窗口
        self.show()

    def addToolItem(self, listWidget, text, iconPath):
        item = QListWidgetItem(QIcon(iconPath), text)
        listWidget.addItem(item)

# 应用程序入口点
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
