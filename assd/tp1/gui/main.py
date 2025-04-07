import sys
import numpy as np
import matplotlib
# Use non-interactive Agg backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                           QGraphicsScene, QVBoxLayout, QWidget, QToolBar,
                           QGraphicsItem, QGraphicsLineItem, QMenu, QDialog,
                           QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QSpinBox, QDoubleSpinBox, QFormLayout,
                           QTabWidget, QSplitter, QMessageBox, QSplashScreen)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPixmap, QIcon

class Port(QGraphicsItem):
    def __init__(self, parent, x, y, is_input=True, is_clock=False):
        super().__init__(parent)
        self.setPos(x, y)
        self.is_input = is_input
        self.is_clock = is_clock
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
            if self.is_clock:
                # Use a different color for clock ports
                painter.setBrush(QBrush(QColor(100, 100, 255)))
            else:
                painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(self.boundingRect())
        
        # Draw port label
        painter.setPen(QPen(Qt.GlobalColor.black))
        if self.is_clock:
            painter.drawText(-12, 5, "Clk")
        elif self.is_input:
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
        # Initialize with a dummy line first
        super().__init__(0, 0, 0, 0)
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
        
        # Update position immediately upon creation
        if end_port:
            self.updatePosition()
        
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
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        
        # Assign a unique ID to each block
        self.id = str(id(self))
        
        # Define block dimensions
        self.width = 100
        self.height = 60
        
        # Define colors for different block types
        self.colors = {
            'FAA': QColor(255, 200, 200),
            'S&H': QColor(200, 255, 200),
            'Clock': QColor(200, 200, 255),
            'Signal': QColor(255, 255, 200),
            'FR': QColor(255, 180, 180),
            'A.Switch': QColor(180, 255, 255),
            'Adder': QColor(255, 200, 255),  # Purple for Adder
            'Noise': QColor(200, 255, 255)   # Cyan for Noise
        }
        
        # Initialize simulation parameters
        self.initialize_simulation_params()
        
        # Create ports
        self.input_ports = []
        self.output_ports = []
        self.clock_ports = []
        
        # Add ports based on block type
        if block_type == 'FAA':
            self.input_ports.append(Port(self, 0, self.height/2, True))
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'S&H':
            self.input_ports.append(Port(self, 0, self.height/2, True))
            self.output_ports.append(Port(self, self.width, self.height/2, False))
            # Add clock port at the top
            clock_port = Port(self, self.width/2, 0, True, True)
            self.clock_ports.append(clock_port)
        elif block_type == 'Clock':
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'Signal':
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'A.Switch':
            self.input_ports.append(Port(self, 0, self.height/2, True))
            self.output_ports.append(Port(self, self.width, self.height/2, False))
            # Add clock port at the top
            clock_port = Port(self, self.width/2, 0, True, True)
            self.clock_ports.append(clock_port)
        elif block_type == 'Adder':
            # Two inputs (top and bottom) and one output
            self.input_ports.append(Port(self, 0, self.height/3, True))
            self.input_ports.append(Port(self, 0, 2*self.height/3, True))
            self.output_ports.append(Port(self, self.width, self.height/2, False))
        elif block_type == 'Noise':
            # No inputs, one output
            self.output_ports.append(Port(self, self.width, self.height/2, False))
    
    def initialize_simulation_params(self):
        if self.block_type == 'Signal':
            self.signal_params = {
                "n_components": 1,
                "frequencies": [1000],
                "amplitude": 1.0
            }
            self.output_signal = None
        elif self.block_type == 'FAA':
            self.filter_params = {
                "cutoff_frequency": 5000
            }
        elif self.block_type == 'Clock':
            self.clock_params = {
                "frequency": 1000,
                "duty_cycle": 50,
                "phase": 0
            }
            self.output_signal = None
        elif self.block_type == 'S&H':
            # Additional params for S&H if needed
            pass
        elif self.block_type == 'A.Switch':
            # Additional params for A.Switch if needed
            pass
        elif self.block_type == 'Noise':
            # Params for noise generator
            self.noise_params = {
                "peak_to_peak": 1.0,
                "noise_type": "white"  # white, pink, etc.
            }
            self.output_signal = None
    
    def generate_signal(self, t):
        """Generate a signal based on block type and parameters"""
        if self.block_type == 'Signal':
            signal = np.zeros_like(t)
            amplitude = self.signal_params["amplitude"] / self.signal_params["n_components"]
            for freq in self.signal_params["frequencies"]:
                signal += amplitude * np.sin(2 * np.pi * freq * t)
            return signal
        
        # For compatibility - redirect to generate_clock if it's a clock
        elif self.block_type == 'Clock':
            return self.generate_clock(t)
            
        # Generate noise if it's a noise block
        elif self.block_type == 'Noise':
            return self.generate_noise(t)
            
        # Default return empty signal
        return np.zeros_like(t)
    
    def generate_noise(self, t):
        """Generate a noise signal based on parameters"""
        if self.block_type == 'Noise':
            # Generate random noise
            noise_type = self.noise_params.get("noise_type", "white")
            peak_to_peak = self.noise_params.get("peak_to_peak", 1.0)
            
            if noise_type == "white":
                # Generate white noise (equal power at all frequencies)
                noise = np.random.normal(0, peak_to_peak/6, size=len(t))  # 6 sigma range for normal distribution
                
                # Scale to desired peak-to-peak
                max_val = np.max(noise)
                min_val = np.min(noise)
                current_pp = max_val - min_val
                
                if current_pp > 0:  # Avoid division by zero
                    noise = noise * (peak_to_peak / current_pp)
                    
                return noise
            
            # Add other noise types here if needed (pink, brown, etc.)
            
        return np.zeros_like(t)
    
    def generate_clock(self, t):
        """Generate a clock signal based on parameters"""
        if self.block_type == 'Clock':
            freq = self.clock_params["frequency"]
            duty = self.clock_params["duty_cycle"] / 100.0
            phase = self.clock_params["phase"] * np.pi / 180.0  # Convert to radians
            period = 1.0 / freq
            # Create square wave with phase offset
            return np.where(((t % period) / period + phase / (2 * np.pi)) % 1.0 < duty, 1.0, 0.0)
        
        # Default return empty signal
        return np.zeros_like(t)
    
    def process_signal(self, input_signal, clock_signal=None):
        """Process input signal based on block type and parameters"""
        if self.block_type == 'FAA':
            # Ideal low-pass filter implementation
            fc = self.filter_params["cutoff_frequency"]
            # Convert to frequency domain
            signal_fft = np.fft.rfft(input_signal)
            # Calculate frequency bins
            freqs = np.fft.rfftfreq(len(input_signal), 1/44100)  # Use default sampling rate
            # Apply filter
            signal_fft[freqs > fc] = 0
            # Convert back to time domain
            return np.fft.irfft(signal_fft, len(input_signal))
            
        elif self.block_type == 'S&H':
            # Sample and hold implementation
            if clock_signal is not None:
                # Create output signal array
                output_signal = np.zeros_like(input_signal)
                
                # Calculate clock frequency from the clock signal
                # Find transitions from low to high to determine period
                transitions = []
                for i in range(1, len(clock_signal)):
                    if clock_signal[i-1] <= 0.5 and clock_signal[i] > 0.5:
                        transitions.append(i)
                
                # Calculate average period in samples
                if len(transitions) > 1:
                    avg_period = np.mean(np.diff(transitions))
                    clock_freq = 44100 / avg_period  # Using default sample rate
                else:
                    # Default if we can't detect
                    clock_freq = 1000
                
                # Process each sample - implement true sample and hold
                last_value = 0
                for i in range(len(clock_signal)):
                    # Detect rising edge of clock (transition from low to high)
                    if i > 0 and clock_signal[i-1] <= 0.5 and clock_signal[i] > 0.5:
                        # At rising edge, sample the input
                        last_value = input_signal[i]
                    
                    # Always output the last sampled value (true sample and hold)
                    output_signal[i] = last_value
                
                # Note: We're no longer applying the sinc envelope in the frequency domain
                # The staircase pattern in the time domain already correctly represents
                # sample-and-hold behavior, and applying the sinc transform was distorting it
                
                return output_signal
            else:
                # If no clock signal, just pass through
                return input_signal
            
        elif self.block_type == 'A.Switch':
            # Analog switch implementation
            if clock_signal is not None:
                # Signal passes through only when clock is high
                # Create output signal array initialized to zeros
                output_signal = np.zeros_like(input_signal)
                
                # For each sample, check if clock is high (>0.5)
                for i in range(len(clock_signal)):
                    if clock_signal[i] > 0.5:
                        # When clock is high, input passes through
                        output_signal[i] = input_signal[i]
                    # When clock is low, output remains zero (already initialized as such)
                
                return output_signal
            else:
                # If no clock signal, just pass through
                return input_signal
        
        elif self.block_type == 'Adder':
            # For the adder, input_signal should be a list of multiple input signals
            if isinstance(input_signal, list) and len(input_signal) >= 2:
                # Verify all signals have the same length
                lengths = [len(sig) for sig in input_signal if sig is not None]
                if not lengths or any(l != lengths[0] for l in lengths):
                    # If signals have different lengths or no valid signals, return zeros
                    return np.zeros_like(input_signal[0]) if input_signal[0] is not None else np.array([])
                
                # Add the signals together
                result = np.zeros_like(input_signal[0])
                for sig in input_signal:
                    if sig is not None:
                        result += sig
                return result
            elif isinstance(input_signal, np.ndarray):
                # If there's only one input signal, return it unchanged
                return input_signal
            else:
                # In case of invalid input, return an empty array
                return np.array([])
                
        # Default case - pass through
        return input_signal
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        # Draw block background
        painter.setBrush(QBrush(self.colors.get(self.block_type, QColor(200, 200, 200))))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawRect(0, 0, self.width, self.height)
        
        # Draw block text
        painter.drawText(10, 30, self.block_type)
        
        # Draw special labels for clock ports if needed
        if self.block_type in ['S&H', 'A.Switch']:
            painter.drawText(int(self.width/2 - 15), 15, "CLK")
        
        # Draw labels for adder inputs
        if self.block_type == 'Adder':
            painter.drawText(5, int(self.height/3) + 5, "In1")
            painter.drawText(5, int(2*self.height/3) + 5, "In2")
            painter.drawText(int(self.width/2 - 10), int(self.height/2) + 5, "+")
        
        # Draw parameter info
        if self.block_type == 'Signal':
            painter.drawText(10, 45, f"n={self.signal_params['n_components']}")
        elif self.block_type == 'FAA':
            painter.drawText(10, 45, f"fc={self.filter_params['cutoff_frequency']}")
        elif self.block_type == 'Clock':
            painter.drawText(10, 45, f"f={self.clock_params['frequency']}")
        elif self.block_type == 'Noise':
            painter.drawText(10, 45, f"Amp={self.noise_params['peak_to_peak']}")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event)
        else:
            super().mousePressEvent(event)
    
    def show_context_menu(self, event):
        menu = QMenu()
        
        if self.block_type == 'Signal':
            config_action = menu.addAction("Configure Signal")
            config_action.triggered.connect(self.configure_signal)
        elif self.block_type == 'FAA':
            config_action = menu.addAction("Configure Filter")
            config_action.triggered.connect(self.configure_filter)
        elif self.block_type == 'Clock':
            config_action = menu.addAction("Configure Clock")
            config_action.triggered.connect(self.configure_clock)
        elif self.block_type == 'Noise':
            config_action = menu.addAction("Configure Noise")
            config_action.triggered.connect(self.configure_noise)
        
        # Show the menu at event position
        menu.exec(event.screenPos())
    
    def configure_signal(self):
        dialog = SignalConfigDialog(signal_params=self.signal_params)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.signal_params = dialog.get_parameters()
            self.update()  # Redraw block to show updated parameters
    
    def configure_filter(self):
        dialog = FAAConfigDialog(filter_params=self.filter_params)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_params = dialog.get_parameters()
            self.update()  # Redraw block to show updated parameters
    
    def configure_clock(self):
        dialog = ClockConfigDialog(clock_params=self.clock_params)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.clock_params = dialog.get_parameters()
            self.update()  # Redraw block to show updated parameters
            
    def configure_noise(self):
        dialog = NoiseConfigDialog(noise_params=self.noise_params)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.noise_params = dialog.get_parameters()
            self.update()  # Redraw block to show updated parameters
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update all connections when block is moved
            for port in self.input_ports + self.output_ports + self.clock_ports:
                for conn in port.connections:
                    conn.updatePosition()
        return super().itemChange(change, value)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.drawing_connection = False
        self.current_connection = None
        self.start_port = None
        
        # Set viewport update mode to ensure proper clearing
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Set background color to very light gray
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # Enable optimizations
        self.setOptimizationFlags(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
            QGraphicsView.OptimizationFlag.DontSavePainterState
        )
        
        # Enable caching
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        
    def drawBackground(self, painter, rect):
        # Fill background with solid color
        painter.fillRect(rect, self.backgroundBrush())
        super().drawBackground(painter, rect)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            items = self.scene().items(pos)
            
            # Process ports first before handling other items
            for item in items:
                if isinstance(item, Port):
                    if not self.drawing_connection:
                        if not item.is_input:  # Can only start connection from output port
                            self.start_port = item
                            self.drawing_connection = True
                            self.current_connection = Connection(item, is_temp=True)
                            self.scene().addItem(self.current_connection)
                            # Update the connection with current mouse position right away
                            self.current_connection.updatePosition(pos)
                            return  # Don't process other items
                    else:
                        if item.is_input and item != self.start_port:  # Can only end at input port
                            # Remove temporary connection
                            if self.current_connection:
                                self.scene().removeItem(self.current_connection)
                            
                            # Create permanent connection
                            new_connection = Connection(self.start_port, item)
                            self.scene().addItem(new_connection)
                            
                            # Add connection to both ports
                            self.start_port.connections.append(new_connection)
                            item.connections.append(new_connection)
                            
                            # Reset connection state
                            self.drawing_connection = False
                            self.current_connection = None
                            self.start_port = None
                            return  # Don't process other items
                            
        # Only process the regular mousePressEvent if we didn't handle a port
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
        if event.button() == Qt.MouseButton.LeftButton and self.drawing_connection and self.current_connection:
            # Check if mouse is over a valid input port
            pos = self.mapToScene(event.pos())
            items = self.scene().items(pos)
            
            valid_port_found = False
            for item in items:
                if isinstance(item, Port) and item.is_input and item != self.start_port:
                    # Create permanent connection
                    new_connection = Connection(self.start_port, item)
                    self.scene().addItem(new_connection)
                    
                    # Add connection to both ports
                    self.start_port.connections.append(new_connection)
                    item.connections.append(new_connection)
                    
                    valid_port_found = True
                    break
            
            # Remove temporary connection regardless of outcome
            if self.current_connection:
                self.scene().removeItem(self.current_connection)
            
            # Reset state
            self.drawing_connection = False
            self.current_connection = None
            self.start_port = None
            
            # If we connected to a valid port, don't pass event to super
            if valid_port_found:
                return
            
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
        self.setWindowIcon(QIcon('AppLogo.png'))  # Set the window icon
        
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
        self.add_block_button(toolbar, "A.Switch", "Analog Switch")
        self.add_block_button(toolbar, "Adder", "Adder")
        self.add_block_button(toolbar, "Noise", "Noise")
        
        # Add simulation toolbar
        sim_toolbar = QToolBar("Simulation Controls")
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, sim_toolbar)
        
        # Add run simulation button
        run_action = sim_toolbar.addAction("Run Simulation")
        run_action.triggered.connect(self.run_simulation)
        
        # Install event filter for key press events
        self.view.installEventFilter(self)
        
        # Simulation parameters
        self.sampling_rate = 44100  # Hz
        self.sim_duration = 1.0     # seconds
        
    def add_block_button(self, toolbar, block_type, tooltip):
        action = toolbar.addAction(block_type)
        action.setToolTip(tooltip)
        action.triggered.connect(lambda: self.add_block(block_type))
        
    def add_block(self, block_type):
        # Get the center point of the view in scene coordinates
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        
        # Define the search area for existing blocks (100x100 rectangle around center)
        search_rect = QRectF(view_center.x() - 50, view_center.y() - 50, 100, 100)
        
        # Check if there are any blocks in the center area
        blocks_in_center = [item for item in self.scene.items(search_rect) 
                          if isinstance(item, Block)]
        
        if blocks_in_center:
            # Center is occupied, create block with offset
            # Calculate offset based on number of existing blocks
            num_blocks = len(blocks_in_center)
            offset_x = 120 * (num_blocks % 3 - 1)  # -120, 0, or 120
            offset_y = 80 * ((num_blocks // 3) % 3 - 1)  # -80, 0, or 80
            
            # Create block at offset position
            block = Block(block_type, view_center.x() + offset_x - 50, 
                        view_center.y() + offset_y - 30)
        else:
            # Center is free, create block at center
            block = Block(block_type, view_center.x() - 50, view_center.y() - 30)
        
        self.scene.addItem(block)
    
    def run_simulation(self):
        # Get all blocks from the scene
        all_blocks = [item for item in self.scene.items() if isinstance(item, Block)]
        
        if not all_blocks:
            print("No blocks to simulate")
            return
        
        print(f"Found {len(all_blocks)} blocks to simulate")
        
        # Parameters for simulation
        duration = 1.0  # seconds
        sampling_rate = 44100
        time_array = np.linspace(0, duration, int(sampling_rate * duration))
        
        # Dictionary to store output signals for each block
        output_signals = {}
        
        # Dictionary to store input signals for each block (for visualization)
        input_connections = {}
        
        # Process source blocks first (Signal, Clock, Noise)
        source_blocks = [block for block in all_blocks if block.block_type in ['Signal', 'Clock', 'Noise']]
        print(f"Found {len(source_blocks)} source blocks")
        
        # Process source blocks
        for block in source_blocks:
            if block.block_type == 'Signal':
                # Generate signal based on parameters
                output_signals[block.id] = block.generate_signal(time_array)
                print(f"Generated signal for block {block.id} (type: {block.block_type})")
            
            elif block.block_type == 'Clock':
                # Generate clock signal based on parameters
                output_signals[block.id] = block.generate_clock(time_array)
                print(f"Generated clock for block {block.id} (type: {block.block_type})")
                
            elif block.block_type == 'Noise':
                # Generate noise signal based on parameters
                output_signals[block.id] = block.generate_noise(time_array)
                print(f"Generated noise for block {block.id} (type: {block.block_type})")
        
        # Sort the remaining blocks to ensure we process in order (simple topological sort)
        remaining_blocks = [block for block in all_blocks if block not in source_blocks]
        print(f"Remaining blocks to process: {len(remaining_blocks)}")
        
        # Store the original input signals for visualization
        raw_input_signals = {}
        
        # Repeat until all blocks are processed or no more can be processed
        processed = set(block.id for block in source_blocks)
        while remaining_blocks:
            blocks_processed_this_round = []
            
            for block in remaining_blocks:
                # Check if all inputs are processed
                all_inputs_ready = True
                input_signal = None
                input_signals = []  # For adder block
                clock_signal = None
                
                # Get all ports
                all_ports = block.input_ports + block.output_ports + block.clock_ports
                
                # Gather input signals from all connected ports
                for port in all_ports:
                    if not port.is_input:  # Skip output ports
                        continue
                    
                    print(f"Processing input port for block {block.id} (type: {block.block_type})")
                    print(f"Port has {len(port.connections)} connections")
                        
                    port_signal = None
                    
                    for conn in port.connections:
                        # Find the source port (the one that is not this port)
                        if conn.end_port == port:
                            # This port is the end/destination of the connection
                            source_port = conn.start_port
                        else:
                            # This port is the start of the connection (unusual case)
                            source_port = conn.end_port
                            
                        source_block = source_port.parentItem()
                        
                        print(f"  Connection from block {source_block.id} (type: {source_block.block_type})")
                        
                        if source_block.id not in processed:
                            all_inputs_ready = False
                            print(f"  Source block not processed yet, skipping")
                            break
                        
                        # Store original input signal for visualization
                        # Only for regular input ports (not clock)
                        if not port.is_clock and source_block.id in output_signals:
                            if block.id not in raw_input_signals:
                                raw_input_signals[block.id] = []
                            raw_input_signals[block.id].append(output_signals[source_block.id])
                        
                        # Store signal based on port type
                        if port.is_clock:
                            clock_signal = output_signals[source_block.id]
                            print(f"  Stored clock signal from block {source_block.id}")
                        else:
                            port_signal = output_signals[source_block.id]
                            print(f"  Stored input signal from block {source_block.id}")
                    
                    # For adder, collect all input signals
                    if block.block_type == 'Adder' and not port.is_clock:
                        input_signals.append(port_signal)
                    elif not port.is_clock:
                        input_signal = port_signal
                
                if all_inputs_ready:
                    # Process the block based on its type
                    if block.block_type == 'FAA':
                        # Apply filter to input
                        if input_signal is not None:
                            # Get FAA parameters from block
                            fc = block.filter_params.get('cutoff_frequency', 1000)  # Default cutoff frequency
                            print(f"Applying FAA filter with fc={fc} Hz")
                            output_signals[block.id] = block.process_signal(input_signal, None)
                        else:
                            # If no input signal, use zeros
                            output_signals[block.id] = np.zeros_like(time_array)
                    
                    elif block.block_type == 'FR':
                        # Process FR block (same as FAA)
                        if input_signal is not None:
                            # Get FR parameters from block
                            fc = block.filter_params.get('cutoff_frequency', 1000)  # Default cutoff frequency
                            print(f"Applying FR filter with fc={fc} Hz")
                            # Convert to frequency domain
                            signal_fft = np.fft.rfft(input_signal)
                            # Calculate frequency bins
                            freqs = np.fft.rfftfreq(len(input_signal), 1/44100)  # Use default sampling rate
                            # Apply filter
                            signal_fft[freqs > fc] = 0
                            # Convert back to time domain
                            return np.fft.irfft(signal_fft, len(input_signal))
                        else:
                            # If no input signal, use zeros
                            return np.zeros_like(input_signal)
                    
                    elif block.block_type in ['S&H', 'A.Switch']:
                        # Process Sample & Hold or Analog Switch
                        if input_signal is not None:
                            print(f"Processing {block.block_type} with input and clock signals")
                            output_signals[block.id] = block.process_signal(input_signal, clock_signal)
                        else:
                            output_signals[block.id] = np.zeros_like(time_array)
                    
                    elif block.block_type == 'Adder':
                        # Process adder with multiple input signals
                        if input_signals:
                            print(f"Processing Adder with {len(input_signals)} input signals")
                            output_signals[block.id] = block.process_signal(input_signals)
                        else:
                            output_signals[block.id] = np.zeros_like(time_array)
                            
                    else:
                        # Generic processing for other block types
                        if input_signal is not None:
                            output_signals[block.id] = block.process_signal(input_signal, None)
                        else:
                            output_signals[block.id] = np.zeros_like(time_array)
                    
                    processed.add(block.id)
                    blocks_processed_this_round.append(block)
                    print(f"Processed block {block.id} (type: {block.block_type})")
            
            # Remove processed blocks from the list
            for block in blocks_processed_this_round:
                remaining_blocks.remove(block)
            
            print(f"Blocks processed this round: {len(blocks_processed_this_round)}")
            print(f"Remaining blocks: {len(remaining_blocks)}")
            
            # If no blocks were processed in this round and there are still remaining blocks,
            # there might be a cyclic dependency or disconnected blocks
            if not blocks_processed_this_round and remaining_blocks:
                print("Warning: Could not process all blocks. Check for cycles or disconnected blocks.")
                break
        
        # Gather input signals from all connected ports
        for block in all_blocks:
            # Create a list to store input signals for this block
            block_inputs = []
            
            for port in block.input_ports:
                for conn in port.connections:
                    # Find the source port
                    if conn.end_port == port:
                        source_port = conn.start_port
                    else:
                        source_port = conn.end_port
                        
                    source_block = source_port.parentItem()
                    if source_block.id in processed:
                        # Store the connection info
                        block_inputs.append(output_signals[source_block.id])
            
            # Store the input signals for visualization
            if block_inputs:
                input_connections[block.id] = block_inputs[0] if len(block_inputs) == 1 else block_inputs
        
        # Show the output signals
        print(f"Showing output signals for {len(output_signals)} blocks")
        
        # Dictionary to store block types and parameters for plotting
        block_info = {}
        for block in all_blocks:
            block_info[block.id] = {'type': block.block_type}
            if block.block_type == 'Signal':
                block_info[block.id]['params'] = block.signal_params
            elif block.block_type == 'FAA':
                block_info[block.id]['params'] = block.filter_params
            elif block.block_type == 'Clock':
                block_info[block.id]['params'] = block.clock_params
            elif block.block_type == 'Noise':
                block_info[block.id]['params'] = block.noise_params
                
        # Pass raw input signals to the viewer for visualization
        viewer = SignalViewerDialog(output_signals, time_array, block_info=block_info, 
                                  raw_input_signals=raw_input_signals)
        viewer.exec()
    
    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress and event.key() == Qt.Key.Key_Delete:
            # Delete selected blocks
            for item in self.scene.selectedItems():
                if isinstance(item, Block):
                    # Remove all connections first
                    for port in item.input_ports + item.output_ports + item.clock_ports:
                        for conn in port.connections[:]:  # Use slice copy to avoid modification during iteration
                            self.scene.removeItem(conn)
                            if conn in port.connections:
                                port.connections.remove(conn)
                    self.scene.removeItem(item)
            return True
        return super().eventFilter(obj, event)

class SignalConfigDialog(QDialog):
    def __init__(self, parent=None, signal_params=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Signal Generator")
        self.signal_params = signal_params or {"n_components": 1, "frequencies": [1000], "amplitude": 1.0}
        
        layout = QVBoxLayout(self)
        
        # Number of sinusoidal components
        form_layout = QFormLayout()
        self.n_components_spin = QSpinBox()
        self.n_components_spin.setRange(1, 10)
        self.n_components_spin.setValue(self.signal_params["n_components"])
        self.n_components_spin.valueChanged.connect(self.update_frequency_fields)
        form_layout.addRow("Number of components:", self.n_components_spin)
        
        # Amplitude
        self.amplitude_spin = QDoubleSpinBox()
        self.amplitude_spin.setRange(0.1, 10.0)
        self.amplitude_spin.setSingleStep(0.1)
        self.amplitude_spin.setValue(self.signal_params["amplitude"])
        form_layout.addRow("Amplitude:", self.amplitude_spin)
        
        layout.addLayout(form_layout)
        
        # Frequencies input
        self.freq_layout = QFormLayout()
        layout.addWidget(QLabel("Frequencies (Hz):"))
        layout.addLayout(self.freq_layout)
        
        # Create initial frequency fields
        self.freq_spinboxes = []
        self.update_frequency_fields()
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def update_frequency_fields(self):
        # Clear existing frequency fields
        for i in reversed(range(self.freq_layout.count())):
            self.freq_layout.itemAt(i).widget().setParent(None)
        
        self.freq_spinboxes = []
        n_components = self.n_components_spin.value()
        
        # Create/update frequency fields
        for i in range(n_components):
            freq_spin = QDoubleSpinBox()
            freq_spin.setRange(1, 100000)
            freq_spin.setSuffix(" Hz")
            
            # Set value from existing params if available
            if i < len(self.signal_params["frequencies"]):
                freq_spin.setValue(self.signal_params["frequencies"][i])
            else:
                freq_spin.setValue(1000 * (i + 1))  # Default to multiples of 1000Hz
                
            self.freq_spinboxes.append(freq_spin)
            self.freq_layout.addRow(f"Frequency {i+1}:", freq_spin)
    
    def get_parameters(self):
        n_components = self.n_components_spin.value()
        frequencies = [spin.value() for spin in self.freq_spinboxes[:n_components]]
        amplitude = self.amplitude_spin.value()
        return {"n_components": n_components, "frequencies": frequencies, "amplitude": amplitude}


class FAAConfigDialog(QDialog):
    def __init__(self, parent=None, filter_params=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Antialiasing Filter")
        self.filter_params = filter_params or {"cutoff_frequency": 5000}
        
        layout = QVBoxLayout(self)
        
        # Cutoff frequency
        form_layout = QFormLayout()
        self.cutoff_spin = QDoubleSpinBox()
        self.cutoff_spin.setRange(1, 100000)
        self.cutoff_spin.setSuffix(" Hz")
        self.cutoff_spin.setValue(self.filter_params["cutoff_frequency"])
        form_layout.addRow("Cutoff frequency:", self.cutoff_spin)
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_parameters(self):
        return {"cutoff_frequency": self.cutoff_spin.value()}


class ClockConfigDialog(QDialog):
    def __init__(self, parent=None, clock_params=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Clock Generator")
        self.clock_params = clock_params or {"frequency": 1000, "duty_cycle": 50, "phase": 0}
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Frequency
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(1, 100000)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setValue(self.clock_params["frequency"])
        form_layout.addRow("Frequency:", self.freq_spin)
        
        # Duty cycle
        self.duty_spin = QSpinBox()
        self.duty_spin.setRange(1, 99)
        self.duty_spin.setSuffix(" %")
        self.duty_spin.setValue(self.clock_params["duty_cycle"])
        form_layout.addRow("Duty cycle:", self.duty_spin)
        
        # Phase
        self.phase_spin = QDoubleSpinBox()
        self.phase_spin.setRange(0, 360)
        self.phase_spin.setSuffix(" °")
        self.phase_spin.setValue(self.clock_params["phase"])
        form_layout.addRow("Phase:", self.phase_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_parameters(self):
        return {
            "frequency": self.freq_spin.value(),
            "duty_cycle": self.duty_spin.value(),
            "phase": self.phase_spin.value()
        }

class SignalViewerDialog(QDialog):
    def __init__(self, signals=None, time_array=None, parent=None, block_info=None, 
                 raw_input_signals=None):
        super().__init__(parent)
        self.setWindowTitle("Signal Viewer")
        self.setMinimumSize(400, 200)
        
        # Store signals and time array
        self.signals = {} if signals is None else signals  # Dict of {block_id: signal_data}
        self.time_array = np.linspace(0, 1, 1000) if time_array is None else time_array
        self.block_info = block_info or {}  # Dict of block information
        self.raw_input_signals = raw_input_signals or {}  # Dict of raw input signals for each block
        
        # Create timestamp for this simulation run
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create a unique folder for this simulation run
        self.output_dir = f"signal_plots/sim_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Information label
        self.label = QLabel(f"Plots saved to {self.output_dir} directory")
        layout.addWidget(self.label)
        
        # List of generated files
        self.file_list = QLabel()
        layout.addWidget(self.file_list)
        
        # Signal list
        if not self.signals:
            layout.addWidget(QLabel("No signals to display"))
        else:
            signal_list = QLabel(f"Generated plots for {len(self.signals)} signals:")
            layout.addWidget(signal_list)
            
            file_list_text = ""
            
            # Save plots for each signal
            for block_id, signal_data in self.signals.items():
                # Get block type and parameters for better naming
                block_type = self.block_info.get(block_id, {}).get('type', "Unknown")
                block_params = self.block_info.get(block_id, {}).get('params', {})
                
                # Create descriptive filename based on block type and parameters
                param_info = ""
                if block_type == 'Signal':
                    freqs = block_params.get('frequencies', [])
                    if freqs:
                        param_info = f"{len(freqs)}freqs_{freqs[0]}Hz"
                elif block_type == 'FAA':
                    param_info = f"fc_{block_params.get('cutoff_frequency', 0)}Hz"
                elif block_type == 'Clock':
                    param_info = f"{block_params.get('frequency', 0)}Hz"
                elif block_type == 'Noise':
                    param_info = f"amp_{block_params.get('peak_to_peak', 1.0)}"
                
                # Create a unique and descriptive filename
                if param_info:
                    filename = f"{self.output_dir}/{block_type}_{param_info}.png"
                else:
                    filename = f"{self.output_dir}/{block_type}_{block_id[-6:]}.png"  # Use last 6 chars of ID
                
                # Create figure
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                # Plot time domain - output signal first
                ax1.plot(self.time_array, signal_data, 'b-', linewidth=2.0, label='Output')
                
                # For S&H blocks, also plot the input signal as a dashed line
                if block_type in ['S&H', 'A.Switch'] and block_id in self.raw_input_signals:
                    # Get the original input signal (first one if multiple)
                    if self.raw_input_signals[block_id]:
                        input_signal = self.raw_input_signals[block_id][0]
                        
                        # Plot the full original input signal
                        ax1.plot(self.time_array, input_signal, 
                                'r--',        # Red dashed line
                                linewidth=1.5, # Slightly thicker
                                alpha=0.7,     # Semi-transparent
                                label='Input')
                        
                        ax1.legend()
                
                ax1.set_title(f"{block_type} - Time Domain{' - ' + param_info if param_info else ''}")
                ax1.set_xlabel("Time (s)")
                ax1.set_ylabel("Amplitude")
                ax1.grid(True)
                
                # Adjust time domain display based on block type
                if block_type == 'Signal':
                    # Try to show 2-3 cycles for signal blocks
                    try:
                        freq = block_params.get('frequencies', [1000])[0]
                        period = 1.0 / freq
                        # Show 3 cycles
                        display_time = 3 * period
                        # Find index closest to display_time
                        idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                        ax1.set_xlim(0, self.time_array[idx-1])
                    except (IndexError, ZeroDivisionError):
                        # Default view if error
                        pass
                
                elif block_type == 'FAA':
                    # For FAA blocks, show time domain based on minimum frequency
                    # First identify if there's frequency content
                    if len(signal_data) > 0:
                        # Compute FFT to find significant frequency components
                        n = len(signal_data)
                        fft_result = np.abs(np.fft.rfft(signal_data)) / n
                        freqs = np.fft.rfftfreq(n, 1/44100)
                        
                        # Find frequencies with significant magnitude (above 1% of max)
                        threshold = np.max(fft_result) * 0.01
                        significant_freqs = freqs[fft_result > threshold]
                        
                        if len(significant_freqs) > 0:
                            # Find minimum significant frequency (exclude near-zero DC component)
                            min_freq = significant_freqs[significant_freqs > 10][0] if len(significant_freqs[significant_freqs > 10]) > 0 else 1000
                            period = 1.0 / min_freq
                            # Show 3 cycles of the minimum frequency
                            display_time = 3 * period
                            # Find index closest to display_time
                            idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                            ax1.set_xlim(0, self.time_array[idx-1])
                            ax1.set_title(f"{block_type} (fc={block_params.get('cutoff_frequency', 'N/A')} Hz) - Time Domain")
                
                elif block_type == 'Clock':
                    # Show a few cycles for clock blocks too
                    try:
                        freq = block_params.get('frequency', 1000)
                        period = 1.0 / freq
                        # Show 3 cycles
                        display_time = 3 * period
                        # Find index closest to display_time
                        idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                        ax1.set_xlim(0, self.time_array[idx-1])
                    except (IndexError, ZeroDivisionError):
                        # Default view if error
                        pass
                
                elif block_type == 'S&H':
                    # For S&H, show 3 cycles of the input signal (not the sampling frequency)
                    try:
                        # Find the fundamental frequency of the signal
                        n = len(signal_data)
                        fft_result = np.abs(np.fft.rfft(signal_data)) / n
                        freqs = np.fft.rfftfreq(n, 1/44100)
                        
                        # Find significant peaks, excluding DC (first bin)
                        peak_threshold = np.max(fft_result[1:]) * 0.1  # 10% of max non-DC
                        peak_indices = np.where(fft_result[1:] > peak_threshold)[0] + 1  # Add 1 to account for skipping DC
                        
                        if len(peak_indices) > 0:
                            # Find the lowest significant frequency peak (fundamental)
                            sorted_peaks = sorted([(freqs[i], fft_result[i]) for i in peak_indices], key=lambda x: x[0])
                            min_freq = sorted_peaks[0][0]
                            
                            # Make sure we have a reasonable frequency
                            if min_freq < 10:  # If freq is too low, might be noise
                                min_freq = 100  # Default to 100Hz
                        else:
                            # If no clear peaks, try to use connected clock info as fallback
                            clock_freq = None
                            for other_id, other_info in self.block_info.items():
                                if other_info.get('type') == 'Clock' and other_id in block_info:
                                    clock_freq = other_info.get('params', {}).get('frequency')
                                    break
                                    
                            # Calculate a reasonable input frequency (half the clock is common)
                            min_freq = clock_freq / 2 if clock_freq else 100  # Default to 100Hz
                        
                        # Calculate time to show 3 cycles of the input frequency
                        period = 1.0 / min_freq
                        display_time = 3 * period
                        
                        # Find index closest to display_time
                        idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                        ax1.set_xlim(0, self.time_array[idx-1])
                        
                        # Add annotation about input and sampling frequencies
                        sampling_freq = clock_freq if 'clock_freq' in locals() else "unknown"
                        ax1.set_title(f"{block_type} - Time Domain (Input={min_freq:.1f}Hz, Fs={sampling_freq}Hz){' - ' + param_info if param_info else ''}")
                    except (IndexError, ZeroDivisionError, ValueError):
                        # Default view if error
                        pass
                
                # Compute and plot frequency domain (simple FFT)
                if len(signal_data) > 0:
                    n = len(signal_data)
                    fft_result = np.abs(np.fft.rfft(signal_data)) / n
                    freqs = np.fft.rfftfreq(n, 1/44100)  # Use default sampling rate
                    
                    # Plot frequency domain with block-specific limits
                    ax2.plot(freqs, fft_result)
                    ax2.set_title(f"{block_type} - Frequency Domain{' - ' + param_info if param_info else ''}")
                    ax2.set_xlabel("Frequency (Hz)")
                    ax2.set_ylabel("Magnitude")
                    ax2.grid(True)
                    
                    # Adjust frequency domain display based on block type
                    if block_type == 'FAA':
                        # For FAA blocks, show up to cutoff frequency + 50%
                        try:
                            fc = block_params.get('cutoff_frequency', 5000)
                            ax2.set_xlim(0, fc * 1.5)  # Show up to 150% of cutoff frequency
                            
                            # Add a vertical line at the cutoff frequency
                            ax2.axvline(x=fc, color='r', linestyle='--', label=f'Cutoff: {fc} Hz')
                            ax2.legend()
                        except (TypeError, ValueError):
                            # Default view if error
                            pass
                    
                    elif block_type == 'Clock':
                        # For clock blocks, show the first 7 harmonics
                        try:
                            freq = block_params.get('frequency', 1000)
                            ax2.set_xlim(0, freq * 7)  # Show 7 harmonics
                            
                            # Mark the fundamental and harmonics
                            for i in range(1, 8):
                                harmonic = freq * i
                                if i == 1:
                                    ax2.axvline(x=harmonic, color='r', linestyle='--', 
                                               label=f'Fundamental: {harmonic} Hz')
                                else:
                                    ax2.axvline(x=harmonic, color='g', linestyle=':', 
                                               alpha=0.5, label=f'Harmonic {i}: {harmonic} Hz')
                            ax2.legend()
                        except (TypeError, ValueError):
                            # Default view if error
                            pass
                    
                    elif block_type == 'Signal':
                        # For signal blocks, show twice the highest frequency component
                        try:
                            freqs_list = block_params.get('frequencies', [1000])
                            max_freq = max(freqs_list) if freqs_list else 1000
                            ax2.set_xlim(0, max_freq * 2)
                            
                            # Mark each frequency component
                            for i, component_freq in enumerate(freqs_list):
                                ax2.axvline(x=component_freq, color='r', linestyle='--', 
                                          label=f'Component {i+1}: {component_freq} Hz')
                            ax2.legend()
                        except (TypeError, ValueError):
                            # Default view if error
                            pass
                    
                    elif block_type == 'S&H':
                        # For S&H, show multiple replicas of the spectrum to visualize the sampling effect
                        try:
                            # Find corresponding clock block
                            clock_freq = None
                            # Look through all blocks to find connected clock
                            for other_id, other_info in self.block_info.items():
                                if other_info.get('type') == 'Clock' and other_id in block_info:
                                    clock_freq = other_info.get('params', {}).get('frequency')
                                    break
                            
                            if not clock_freq:
                                # If no clock found, try to estimate from spectral content
                                # Find peaks in the spectrum
                                peak_indices = np.argsort(fft_result)[-10:]  # Get indices of top 10 peaks
                                peak_freqs = [freqs[idx] for idx in peak_indices if idx < len(freqs)]
                                
                                if peak_freqs:
                                    # Try to find regular spacing between peaks (clock frequency)
                                    peak_diffs = np.diff(sorted(peak_freqs))
                                    if len(peak_diffs) > 0:
                                        # Use the most common difference as estimate of clock frequency
                                        clock_freq = np.median(peak_diffs)
                                    else:
                                        clock_freq = 1000  # Default
                                else:
                                    clock_freq = 1000  # Default
                            
                            # Show 4x the clock frequency to see multiple replicas
                            ax2.set_xlim(0, clock_freq * 4.5)
                            
                            # Draw vertical lines at the clock frequency and its multiples
                            for i in range(1, 5):
                                harmonic = clock_freq * i
                                if i == 1:
                                    ax2.axvline(x=harmonic, color='r', linestyle='--', 
                                               label=f'Clock: {harmonic:.1f} Hz')
                                else:
                                    ax2.axvline(x=harmonic, color='g', linestyle=':', 
                                               alpha=0.7, label=f'{i}×Clock: {harmonic:.1f} Hz')
                            
                            # Sinc envelope visualization is removed, but processing is still applied
                            
                            ax2.legend()
                            ax2.set_title(f"{block_type} - Frequency Domain (with spectral replicas){' - ' + param_info if param_info else ''}")
                        except (IndexError, ValueError):
                            ax2.set_xlim(0, 5000)  # Default range
                    
                    elif block_type == 'A.Switch':
                        # For A.Switch, show 3 cycles of the input signal's minimum frequency
                        try:
                            # Find the fundamental frequency of the input signal
                            if block_id in self.raw_input_signals:
                                input_signal = self.raw_input_signals[block_id][0]  # Use the first input signal
                                n = len(input_signal)
                                fft_result = np.abs(np.fft.rfft(input_signal)) / n
                                freqs = np.fft.rfftfreq(n, 1/44100)

                                # Find significant peaks, excluding DC (first bin)
                                peak_threshold = np.max(fft_result[1:]) * 0.1  # 10% of max non-DC
                                peak_indices = np.where(fft_result[1:] > peak_threshold)[0] + 1  # Add 1 to account for skipping DC

                                if len(peak_indices) > 0:
                                    # Find the lowest significant frequency peak (fundamental)
                                    sorted_peaks = sorted([(freqs[i], fft_result[i]) for i in peak_indices], key=lambda x: x[0])
                                    min_freq = sorted_peaks[0][0]

                                    # Make sure we have a reasonable frequency
                                    if min_freq < 10:  # If freq is too low, might be noise
                                        min_freq = 100  # Default to 100Hz
                                    else:
                                        min_freq = 100  # Default to 100Hz

                                # Calculate time to show 3 cycles of the input frequency
                                period = 1.0 / min_freq
                                display_time = 3 * period

                                # Find index closest to display_time
                                idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                                ax1.set_xlim(0, self.time_array[idx-1])

                                ax1.set_title(f"{block_type} - Time Domain (Input={min_freq:.1f}Hz){' - ' + param_info if param_info else ''}")
                        except (IndexError, ZeroDivisionError, ValueError):
                            # Default view if error
                            pass
                    
                    elif block_type == 'Adder':
                        # For Adder blocks, try to show a reasonable frequency range
                        try:
                            # Find peak frequencies in the spectrum
                            peak_indices = np.argsort(fft_result)[-5:]  # Get indices of top 5 peaks
                            if len(peak_indices) > 0:
                                highest_freq = max(freqs[idx] for idx in peak_indices if idx < len(freqs))
                                ax2.set_xlim(0, highest_freq * 1.5)  # Show 1.5x the highest peak frequency
                                
                                # Mark the most significant peak frequencies
                                for i, idx in enumerate(reversed(peak_indices)):
                                    if idx < len(freqs):
                                        ax2.axvline(x=freqs[idx], color='r' if i == 0 else 'g', 
                                                   linestyle='--', alpha=0.7,
                                                   label=f'Peak {i+1}: {freqs[idx]:.1f} Hz')
                                ax2.legend()
                            else:
                                ax2.set_xlim(0, 10000)  # Default range
                            
                            # In time domain, show four cycles of the lowest frequency from both inputs
                            if block_id in self.raw_input_signals:
                                # Get both input signals
                                input_signals = self.raw_input_signals[block_id]
                                
                                # Find the lowest frequency in each input signal
                                min_freqs = []
                                for input_signal in input_signals:
                                    if input_signal is not None:
                                        n = len(input_signal)
                                        fft_result = np.abs(np.fft.rfft(input_signal)) / n
                                        freqs = np.fft.rfftfreq(n, 1/44100)
                                        
                                        # Find significant peaks, excluding DC (first bin)
                                        peak_threshold = np.max(fft_result[1:]) * 0.1  # 10% of max non-DC
                                        peak_indices = np.where(fft_result[1:] > peak_threshold)[0] + 1
                                        
                                        if len(peak_indices) > 0:
                                            # Find the lowest significant frequency peak
                                            sorted_peaks = sorted([(freqs[i], fft_result[i]) for i in peak_indices], key=lambda x: x[0])
                                            min_freq = sorted_peaks[0][0]
                                            
                                            # Make sure we have a reasonable frequency
                                            if min_freq >= 10:  # Only consider frequencies above 10 Hz
                                                min_freqs.append(min_freq)
                                
                                if min_freqs:
                                    # Use the lowest frequency among all inputs
                                    lowest_freq = min(min_freqs)
                                    period = 1.0 / lowest_freq
                                    # Show 4 cycles
                                    display_time = 4 * period
                                    # Find index closest to display_time
                                    idx = min(len(self.time_array), max(1, int(display_time / (self.time_array[1] - self.time_array[0]))))
                                    ax1.set_xlim(0, self.time_array[idx-1])
                                    
                                    # Add annotation about the frequency
                                    ax1.set_title(f"{block_type} - Time Domain (4 cycles of {lowest_freq:.1f}Hz){' - ' + param_info if param_info else ''}")
                        except (IndexError, ZeroDivisionError, ValueError):
                            # Default view if error
                            pass
                    
                    elif block_type == 'Noise':
                        # For Noise blocks, show a wide spectrum
                        try:
                            # Show up to Nyquist frequency (half of sampling rate)
                            nyquist = 44100 / 2  # Assuming 44.1 kHz sampling rate
                            ax2.set_xlim(0, nyquist)
                            
                            # Add peak-to-peak annotation
                            peak_to_peak = block_params.get('peak_to_peak', 1.0)
                            ax2.set_title(f"{block_type} (Amp={peak_to_peak}) - Frequency Domain{' - ' + param_info if param_info else ''}")
                            
                            # In time domain, show appropriate amplitude range
                            ax1.set_ylim(-peak_to_peak/2, peak_to_peak/2)
                            ax1.set_title(f"{block_type} (Amp={peak_to_peak}) - Time Domain{' - ' + param_info if param_info else ''}")
                        except (TypeError, ValueError):
                            # Default view if error
                            pass
                    
                    else:
                        # Generic display for other block types
                        # Limit to a reasonable range (e.g., 10 kHz)
                        ax2.set_xlim(0, 10000)
                
                plt.tight_layout()
                plt.savefig(filename)
                plt.close(fig)
                
                file_list_text += f"{block_type} {param_info}: {os.path.basename(filename)}\n"
            
            # Show list of generated files
            self.file_list.setText(file_list_text)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
        # Show a message box
        QMessageBox.information(self, "Plots Generated", 
                              f"Signal plots have been saved to the '{self.output_dir}' directory.\n"
                              f"Total signals processed: {len(self.signals)}")

class NoiseConfigDialog(QDialog):
    def __init__(self, parent=None, noise_params=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Noise Generator")
        self.noise_params = noise_params or {"peak_to_peak": 1.0, "noise_type": "white"}
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Peak-to-peak amplitude
        self.peak_to_peak_spin = QDoubleSpinBox()
        self.peak_to_peak_spin.setRange(0.01, 10.0)
        self.peak_to_peak_spin.setSingleStep(0.1)
        self.peak_to_peak_spin.setValue(self.noise_params["peak_to_peak"])
        form_layout.addRow("Peak-to-peak amplitude:", self.peak_to_peak_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_parameters(self):
        return {
            "peak_to_peak": self.peak_to_peak_spin.value(),
            "noise_type": "white"  # Only white noise for now
        }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create and display the splash screen with a further scaled logo
    splash_pix = QPixmap('AppLogo.png')
    splash_pix = splash_pix.scaled(splash_pix.width() // 4, splash_pix.height() // 4, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # Create the main window
    window = MainWindow()
    
    # Set up a timer to close the splash screen and show the main window
    QTimer.singleShot(3000, lambda: (splash.close(), window.show()))  # 3000 ms = 3 seconds
    
    sys.exit(app.exec())
