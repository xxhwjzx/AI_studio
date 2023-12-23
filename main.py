import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QDockWidget, QListWidget, QGraphicsItem, QPushButton
from PyQt5.QtCore import Qt, QRectF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Training and Inference Workstation')
        self.setGeometry(100, 100, 1200, 800)

        # 创建图形视图和场景
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # 创建工具箱
        self.createDockWidgets()

        # 设置场景范围
        self.scene.setSceneRect(QRectF(self.view.viewport().rect()))

    def createDockWidgets(self):
        # 工具箱
        dock = QDockWidget("Tools", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        toolbox = QListWidget()
        toolbox.addItems(["Data Source", "Preprocessing", "Model", "Evaluation"])
        dock.setWidget(toolbox)

        # 控件点击事件，可以拖拽到场景中
        toolbox.itemDoubleClicked.connect(self.toolboxItemDoubleClicked)

    def toolboxItemDoubleClicked(self, item):
        # 这里将添加创建和放置控件到场景中的逻辑
        print(f"{item.text()} double clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
