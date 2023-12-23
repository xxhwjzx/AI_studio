from PyQt5.QtCore import QLineF, QPoint
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QListWidget, QGraphicsItem
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QDrag

from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF

class IconGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, itemType, parent=None):
        super().__init__(pixmap, parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.itemType = itemType
        self.addConnectorPoints()

    def addConnectorPoints(self):
        point_size = 10
        # 根据模块类型添加连接点
        if self.itemType == "输入数据":
            # 只有一个输出点
            self.addOutputPoint(point_size)
        elif self.itemType == "处理模块":
            # 既有输入点也有输出点
            self.addInputPoint(point_size)
            self.addOutputPoint(point_size)
        # 根据需要添加更多类型的判断和处理

    def addInputPoint(self, point_size):
        connector_point_x = -point_size / 2  # 输入点在图标左侧
        connector_point_y = self.boundingRect().height() / 2 - point_size / 2
        input_point = QGraphicsEllipseItem(QRectF(connector_point_x, connector_point_y, point_size, point_size), self)
        input_point.setBrush(QBrush(QColor(Qt.red)))  # 输入点用红色表示
        self.input_point = input_point  # 保存引用以便后续使用

    def addOutputPoint(self, point_size):
        connector_point_x = self.boundingRect().width() - point_size / 2  # 输出点在图标右侧
        connector_point_y = self.boundingRect().height() / 2 - point_size / 2
        output_point = QGraphicsEllipseItem(QRectF(connector_point_x, connector_point_y, point_size, point_size), self)
        output_point.setBrush(QBrush(QColor(Qt.green)))  # 输出点用绿色表示
        self.output_point = output_point  # 保存引用以便后续使用


class GridGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(GridGraphicsScene, self).__init__(parent)
        self.setSceneRect(0, 0, 8000, 6000)  # 根据需要设置场景大小

    def drawBackground(self, painter, rect):
        # 在场景中绘制网格
        grid_interval = 20  # 步长设置为整数
        left = int(rect.left()) - (int(rect.left()) % grid_interval)
        top = int(rect.top()) - (int(rect.top()) % grid_interval)

        # 创建网格线的路径
        lines = []
        for x in range(left, int(rect.right()), grid_interval):
            lines.append(QLineF(QPointF(x, rect.top()), QPointF(x, rect.bottom())))
        for y in range(top, int(rect.bottom()), grid_interval):
            lines.append(QLineF(QPointF(rect.left(), y), QPointF(rect.right(), y)))

        # 绘制网格线
        painter.setPen(QPen(Qt.lightGray, 1))
        painter.drawLines(lines)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        pos = event.scenePos()
        text = event.mimeData().text()
        self.addCustomItem(text, pos)
        event.acceptProposedAction()  # 确保事件被接受

    def addCustomItem(self, text, pos):
        # 根据拖放的文本和位置添加自定义图形项
        # 示例: 根据 text 创建不同的图形项
        if text == "输入数据":
            icon_pixmap = QIcon("resources/icons/input_data.png").pixmap(50, 50)
            icon_item = IconGraphicsItem(icon_pixmap, "输入数据")  # 指定类型为 "输入数据"
            icon_item.setPos(pos - QPointF(icon_pixmap.width() / 2, icon_pixmap.height() / 2))
            self.addItem(icon_item)
        elif text == "Preprocessing":
            # 添加预处理图形项
            pass
        # 其他类似处理



class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(ZoomableGraphicsView, self).__init__(scene, parent)
        self.setDragMode(QGraphicsView.NoDrag)
        self._isPanning = False
        self._panStartPos = QPoint()
        self.viewport().setCursor(Qt.ArrowCursor)  # 设置默认光标
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        # 滚轮事件来实现缩放
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # 保存当前的缩放状态
        oldPos = self.mapToScene(event.pos())

        # 执行缩放
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # 获取缩放后的位置
        newPos = self.mapToScene(event.pos())

        # 移动场景到新位置
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                # 如果鼠标点击的位置没有项，开始拖动场景
                self._isPanning = True
                self._panStartPos = event.pos()
                self.viewport().setCursor(Qt.ClosedHandCursor)
                event.accept()
            else:
                super(ZoomableGraphicsView, self).mousePressEvent(event)
        else:
            super(ZoomableGraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._isPanning:
            # 实现拖动功能
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStartPos.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStartPos.y()))
            self._panStartPos = event.pos()
            event.accept()
        else:
            super(ZoomableGraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._isPanning:
                self._isPanning = False
                self.viewport().setCursor(Qt.ArrowCursor)
                event.accept()
            else:
                super(ZoomableGraphicsView, self).mouseReleaseEvent(event)
        else:
            super(ZoomableGraphicsView, self).mouseReleaseEvent(event)



class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.setDragEnabled(True)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        currentItem = self.currentItem()
        if currentItem is None:
            return

        # Create a pixmap from the item's icon
        icon = currentItem.icon()
        pixmap = icon.pixmap(50, 50)  # Assuming icon size is 50x50

        # Start the drag
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(currentItem.text())  # Set the text to be used in drop
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction)  # 确保开始了拖拽操作