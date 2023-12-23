from PyQt5.QtCore import QLineF, QPoint
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QIcon, QBrush, QColor, QTransform, QCursor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QListWidget, QGraphicsItem, QGraphicsTextItem, QInputDialog, \
    QGraphicsLineItem
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QDrag

from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF


class ConnectionLine(QGraphicsLineItem):
    def __init__(self, start_item, end_item=None, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.setPen(QPen(Qt.black, 2))
        self.updatePosition()
        self.closest_input_connector = None
        print("ConnectionLine created")

    def updatePosition(self):
        print(f"updatePosition called, line in scene: {'yes' if self.scene() else 'no'}")
        if self.scene():
            if self.start_item and not self.end_item:
                start_pos = self.start_item.scenePos()
                end_pos = self.scene().views()[0].mapToScene(
                    self.scene().views()[0].mapFromGlobal(QCursor.pos()))
                print(f"Updating line: start={start_pos}, end={end_pos} (follow mouse)")
                self.setLine(QLineF(start_pos, end_pos))
                # 检测并更新最接近的输入连接点
                self.updateClosestInputConnector(end_pos)
            elif self.start_item and self.end_item:
                start_pos = self.start_item.scenePos()
                end_pos = self.end_item.scenePos()
                print(f"Finalizing line: start={start_pos}, end={end_pos}")
                self.setLine(QLineF(start_pos, end_pos))
        else:
            print("ConnectionLine not in scene, skipping updatePosition")


    def updateClosestInputConnector(self, pos):
        min_distance = float('inf')
        closest_connector = None
        for connector in self.scene().getInputConnectors():
            distance = (connector.scenePos() - pos).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_connector = connector

        # 如果有一个接近的输入连接点，更新其外观
        if closest_connector and min_distance < 50:  # 50是接近的阈值，可以根据需要调整
            if self.closest_input_connector != closest_connector:
                if self.closest_input_connector:
                    self.resetInputConnectorAppearance(self.closest_input_connector)
                closest_connector.setBrush(QBrush(Qt.blue))  # 改变颜色
                closest_connector.setScale(1.5)  # 放大
                self.closest_input_connector = closest_connector
        else:
            if self.closest_input_connector:
                self.resetInputConnectorAppearance(self.closest_input_connector)
                self.closest_input_connector = None

    @staticmethod
    def resetInputConnectorAppearance(connector):
        connector.setBrush(QBrush(Qt.red))  # 恢复原始颜色
        connector.setScale(1)  # 恢复原始大小
class EditableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setDefaultTextColor(Qt.white)  # 设置文本颜色为白色
        self.setTextInteractionFlags(Qt.NoTextInteraction)  # 默认禁止文本交互
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)  # 禁止获取焦点，防止出现虚线框
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            old_text = self.toPlainText()
            new_text, ok = QInputDialog.getText(None, "Edit Text", "Enter new name:", text=old_text)
            if ok and new_text and new_text != old_text:
                self.setPlainText(new_text)
                self.updatePosition()  # 更新位置
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def updatePosition(self):
        # 计算新位置以使文本居中对齐于图标下方
        parent_item = self.parentItem()
        if parent_item:
            text_width = self.boundingRect().width()
            parent_width = parent_item.boundingRect().width()
            new_x = (parent_width - text_width) / 2
            new_y = parent_item.boundingRect().height()  # 根据需要调整这个值来放置文本
            self.setPos(new_x, new_y)



class IconGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, itemType, parent=None):
        super().__init__(pixmap, parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.itemType = itemType
        self.addConnectorPoints()
        # self.addTextLabel(itemType)
        self.connected_lines = []  # 初始化空列表以存储连接线

    def addConnectorPoints(self):
        point_size = 100
        # 根据模块类型添加连接点
        if self.itemType == "输入数据":
            print("Adding output point to 输入数据")
            self.addOutputPoint(point_size)
        elif self.itemType == "预处理":
            print("Adding input and output points to 预处理")
            self.addInputPoint(point_size)
            self.addOutputPoint(point_size)
        # 根据需要添加更多类型的判断和处理

    def addInputPoint(self, point_size):
        input_point = InputConnector(self)
        local_pos = QPointF(-point_size / 2, self.boundingRect().height() / 2 - point_size / 2)
        input_point.setPos(local_pos)  # 直接设置相对于父项的局部坐标
        self.input_point = input_point
        print(f"Input point added at {input_point.pos()} (relative to parent)")

    def addOutputPoint(self, point_size):
        output_point = OutputConnector(self)
        local_pos = QPointF(self.boundingRect().width() - point_size / 2,
                            self.boundingRect().height() / 2 - point_size / 2)
        output_point.setPos(local_pos)  # 直接设置相对于父项的局部坐标
        self.output_point = output_point
        self.printOutputPointScenePosition()  # 调用打印方法

    def printOutputPointScenePosition(self):
        if self.scene() and hasattr(self, 'output_point'):
            # 打印局部坐标和场景坐标
            local_pos = self.output_point.pos()
            scene_pos = self.mapToScene(local_pos)
            print(f"Output point added at {local_pos} (relative to parent), Scene Position: {scene_pos}")

    # def itemChange(self, change, value):
    #     if change == QGraphicsItem.ItemScenePositionHasChanged:
    #         for line in self.connected_lines:
    #             line.updatePosition()
    #     elif change == QGraphicsItem.ItemSceneHasChanged:
    #         self.updateConnectorPositions()
    #     return super().itemChange(change, value)
    def itemChange(self, change, value):
        result = super().itemChange(change, value)
        if change == QGraphicsItem.ItemSceneHasChanged or change == QGraphicsItem.ItemScenePositionHasChanged:
            self.printOutputPointScenePosition()
        return result
    def updateConnectorPositions(self):
        if hasattr(self, 'input_point'):
            # 更新输入连接点的位置
            input_local_pos = QPointF(-50 / 2, self.boundingRect().height() / 2 - 50 / 2)
            self.input_point.setPos(self.mapToScene(input_local_pos))

        if hasattr(self, 'output_point'):
            # 更新输出连接点的位置
            output_local_pos = QPointF(self.boundingRect().width() - 50 / 2,
                                       self.boundingRect().height() / 2 - 50 / 2)
            self.output_point.setPos(self.mapToScene(output_local_pos))

    def addTextLabel(self, itemType):
        # 现在，这个方法将在项目已经添加到场景之后被调用
        unique_name = self.generateUniqueName(itemType)
        self.textItem = EditableTextItem(unique_name, self)
        # 调整文本项的位置到图标下方
        text_pos = QPointF(self.boundingRect().width() / 2 - self.textItem.boundingRect().width() / 2,
                           self.boundingRect().height())
        self.textItem.setPos(text_pos)

    # 可选：在删除项时清理连接线
    def remove(self):
        for line in self.connected_lines:
            if line.scene():
                line.scene().removeItem(line)
        self.scene().removeItem(self)

    def generateUniqueName(self, baseName):
        # 检查场景中是否已经存在该名称，并生成唯一的名称
        existing_names = [item.toPlainText() for item in self.scene().items() if isinstance(item, EditableTextItem)]
        count = 1
        unique_name = f"{baseName}{count}"
        while unique_name in existing_names:
            count += 1
            unique_name = f"{baseName}{count}"
        return unique_name


class Connector(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRect(-50, -50, 100, 100)  # 设置连接点的大小
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)  # 使连接点能够发送位置变化信号
class OutputConnector(Connector):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBrush(QBrush(QColor(Qt.green)))

class InputConnector(Connector):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBrush(QBrush(QColor(Qt.red)))


class GridGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(GridGraphicsScene, self).__init__(parent)
        self.setSceneRect(0, 0, 8000, 6000)  # 根据需要设置场景大小
        self.current_line = None  # 初始化 current_line 属性

    def getInputConnectors(self):
        return [item for item in self.items() if isinstance(item, InputConnector)]

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
        if text == "输入数据":
            icon_pixmap = QIcon("resources/icons/input_data.png").pixmap(50, 50)
            icon_item = IconGraphicsItem(icon_pixmap, "输入数据")
            icon_item.setPos(pos - QPointF(icon_pixmap.width() / 2, icon_pixmap.height() / 2))
            self.addItem(icon_item)  # 将图形项添加到场景中
            icon_item.addTextLabel("输入数据")  # 现在可以添加文本标签
        elif text == "预处理":
            icon_pixmap = QIcon("resources/icons/preprocess.png").pixmap(50, 50)
            icon_item = IconGraphicsItem(icon_pixmap, "预处理")
            icon_item.setPos(pos - QPointF(icon_pixmap.width() / 2, icon_pixmap.height() / 2))
            self.addItem(icon_item)  # 将图形项添加到场景中
            icon_item.addTextLabel("预处理")  # 现在可以添加文本标签
        # 其他类似处理

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if isinstance(item, OutputConnector):
            print("Mouse pressed on OutputConnector")
            self.current_line = ConnectionLine(item.parentItem())
            self.addItem(self.current_line)
            self.current_line.updatePosition()
        else:
            print("Mouse pressed on non-connector item or empty space")
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_line:
            print("Mouse move with active connection line")
            p1 = self.current_line.start_item.scenePos()
            p2 = event.scenePos()
            self.current_line.setLine(QLineF(p1, p2))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.current_line:
            print("Mouse released")
            end_item = self.itemAt(event.scenePos(), QTransform())
            print(f"Mouse released on item: {type(end_item)} at position {event.scenePos()}")
            if isinstance(end_item, InputConnector):
                print("Mouse released on InputConnector")
                self.current_line.end_item = end_item.parentItem()
                self.current_line.updatePosition()
                start_item = self.current_line.start_item
                start_item.connected_lines.append(self.current_line)
                end_item.parentItem().connected_lines.append(self.current_line)
            else:
                print("Mouse released on non-connector item or empty space, removing line")
                self.removeItem(self.current_line)
            self.current_line = None
        else:
            super().mouseReleaseEvent(event)


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