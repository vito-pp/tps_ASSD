import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                           QGraphicsScene, QVBoxLayout, QWidget, QToolBar,
                           QGraphicsItem, QGraphicsLineItem)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter

class Port(QGraphicsItem):
    def __init__(self, parent, x, y, is_input=True):
        super().__init__(parent)
        self.setPos(x, y)
        self.is_input = is_input
        self.setAcceptHoverEvents(True)
        self.connections = []
        self.radius = 8
        self.hovered = False
        self.can_connect = False
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
    
    def paint(self, painter, option, widget):
        # Draw outer circle (larger when hovered)
        outer_radius = self.radius + 2 if self.hovered else self.radius
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(QRectF(-outer_radius, -outer_radius, 2*outer_radius, 2*outer_radius))
        
        # Draw inner circle with color based on state
        if self.can_connect:
            painter.setPen(QPen(Qt.GlobalColor.green, 2))
            painter.setBrush(QBrush(Qt.GlobalColor.green))
        else:
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(self.boundingRect())
        
        # Draw port label
        painter.setPen(QPen(Qt.GlobalColor.black))
        if self.is_input:
            painter.drawText(-20, 5, "In")
        else:
            painter.drawText(10, 5, "Out")
        
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.can_connect = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def scenePos(self):
        return self.mapToScene(QPointF(0, 0))

class Connection(QGraphicsLineItem):
    def __init__(self, start_port, end_port=None, is_temp=False):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.is_temp = is_temp
        # Make temporary connections dashed and blue
        if is_temp:
            pen = QPen(QColor(0, 0, 255), 2, Qt.PenStyle.DashLine)
        else:
            pen = QPen(Qt.GlobalColor.black, 2)
        self.setPen(pen)
        self.setZValue(1)  # Changed from -1 to 1 to ensure connections are visible
        
    def updatePosition(self, mouse_pos=None):
        if self.end_port:
            start_pos = self.start_port.scenePos()
            end_pos = self.end_port.scenePos()
            self.setLine(start_pos.x(), start_pos.y(),
                        end_pos.x(), end_pos.y())
        elif self.start_port and mouse_pos:
            # For temporary connections, use the provided mouse position
            start_pos = self.start_port.scenePos()
            self.setLine(start_pos.x(), start_pos.y(),
                        mouse_pos.x(), mouse_pos.y())

class Block(QGraphicsItem):
    def __init__(self, block_type, x, y):
        super().__init__()
        self.block_type = block_type
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Define block dimensions
        self.width = 100
        self.height = 60
        
        # Define colors for different block types
        self.colors = {
            'FAA': QColor(255, 200, 200),
            'S&H': QColor(200, 255, 200),
            'Clock': QColor(200, 200, 255),
            'Signal': QColor(255, 255, 200)
        }
        
        # Create ports
        self.input_ports = []
        self.output_ports = []
        
        # Add ports based on block type
        if block_type in ['FAA', 'S&H']:
            self.input_ports.append(Port(self, 0, self.height/2, True))
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'Clock':
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'Signal':
            self.output_ports.append(Port(self, self.width, self.height/2, False))
            
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        # Draw block background
        painter.setBrush(QBrush(self.colors.get(self.block_type, QColor(200, 200, 200))))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawRect(0, 0, self.width, self.height)
        
        # Draw block text
        painter.drawText(10, 30, self.block_type)
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Update all connections when block is moved
        for port in self.input_ports + self.output_ports:
            for conn in port.connections:
                conn.updatePosition()

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.drawing_connection = False
        self.current_connection = None
        self.start_port = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            items = self.scene().items(pos)
            for item in items:
                if isinstance(item, Port):
                    if not self.drawing_connection:
                        if not item.is_input:  # Can only start connection from output port
                            self.start_port = item
                            self.drawing_connection = True
                            self.current_connection = Connection(item, is_temp=True)
                            self.scene().addItem(self.current_connection)
                    else:
                        if item.is_input and item != self.start_port:  # Can only end at input port
                            # Remove temporary connection
                            if self.current_connection:
                                self.scene().removeItem(self.current_connection)
                            
                            # Create permanent connection
                            new_connection = Connection(self.start_port, item)
                            self.scene().addItem(new_connection)
                            new_connection.updatePosition()
                            
                            # Add connection to both ports
                            self.start_port.connections.append(new_connection)
                            item.connections.append(new_connection)
                            
                            # Reset connection state
                            self.drawing_connection = False
                            self.current_connection = None
                            self.start_port = None
                            return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.drawing_connection and self.current_connection:
            pos = self.mapToScene(event.pos())
            self.current_connection.updatePosition(pos)
            
            # Check if we're hovering over a valid input port
            items = self.scene().items(pos)
            for item in items:
                if isinstance(item, Port):
                    if item.is_input and item != self.start_port:
                        item.can_connect = True
                        item.update()
                    else:
                        item.can_connect = False
                        item.update()
        else:
            # Reset all ports' can_connect state
            for item in self.scene().items():
                if isinstance(item, Port):
                    item.can_connect = False
                    item.update()
                    
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if self.drawing_connection and self.current_connection:
            # If we release without connecting to a valid port, remove the temporary connection
            self.scene().removeItem(self.current_connection)
            self.drawing_connection = False
            self.current_connection = None
            self.start_port = None
            
            # Reset all ports' can_connect state
            for item in self.scene().items():
                if isinstance(item, Port):
                    item.can_connect = False
                    item.update()
                    
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sampling Circuit Simulator")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Create scene and view
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.view)
        
        # Add blocks to toolbar
        self.add_block_button(toolbar, "FAA", "Antialiasing Filter")
        self.add_block_button(toolbar, "S&H", "Sample and Hold")
        self.add_block_button(toolbar, "Clock", "Clock Generator")
        self.add_block_button(toolbar, "Signal", "Signal Generator")
        
        # Install event filter for key press events
        self.view.installEventFilter(self)
        
    def add_block_button(self, toolbar, block_type, tooltip):
        action = toolbar.addAction(block_type)
        action.setToolTip(tooltip)
        action.triggered.connect(lambda: self.add_block(block_type))
        
    def add_block(self, block_type):
        block = Block(block_type, 0, 0)
        self.scene.addItem(block)
        
    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress and event.key() == Qt.Key.Key_Delete:
            # Delete selected blocks
            for item in self.scene.selectedItems():
                if isinstance(item, Block):
                    # Remove all connections first
                    for port in item.input_ports + item.output_ports:
                        for conn in port.connections[:]:  # Use slice copy to avoid modification during iteration
                            self.scene.removeItem(conn)
                            if conn in port.connections:
                                port.connections.remove(conn)
                    self.scene.removeItem(item)
            return True
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
