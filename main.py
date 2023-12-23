# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.mainwindow import MainWindow
import qtmodern.styles
import qtmodern.windows
from PyQt5.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)
    # 设置全局字体大小
    font = app.font()
    font.setPointSize(14)
    app.setFont(font)
    # 设置全局控件大小
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    window = MainWindow()
    modern_window = qtmodern.windows.ModernWindow(window)
    modern_window.showMaximized()  # 在这里调用 showMaximized
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
