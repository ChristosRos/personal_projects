import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import json 
import socket
import numpy as np
from PyQt5.QtCore import QTimer


class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Plotting with PyQt")
        self.setGeometry(100, 100, 1024, 720)

        # Initialize GUI elements
        self.ip_address_label = QLabel("IP Address:")
        self.ip_address_lineedit = QLineEdit()
        self.duration_label = QLabel("Duration (s):")
        self.duration_lineedit = QLineEdit()
        self.jrpc_label = QLabel("JRPC Port")
        self.jrpc_lineedit = QLineEdit()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        # Initialize plotting variables
        self.x_data = []
        self.y_data = []
        self.plot_interval = 100  # milliseconds
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)

        # Set up layout
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox1.addWidget(self.ip_address_label)
        hbox1.addWidget(self.ip_address_lineedit)
        hbox1.addWidget(self.duration_label)
        hbox1.addWidget(self.duration_lineedit)
        hbox1.addWidget(self.jrpc_label)
        hbox1.addWidget(self.jrpc_lineedit)
        hbox2.addWidget(self.start_button)
        hbox2.addWidget(self.stop_button)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        # Set up the figure and canvas for the plot
        self.figure = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

        # Connect the start and stop button signals to their respective slots
        self.start_button.clicked.connect(self.start_plotting)
        self.stop_button.clicked.connect(self.stop_plotting)

        #self.y_data = np.zeros((100,))
        #self.timer = QTimer() 
        #self.timer.timeout.connect(self.update_plot)

    def send_and_receive(self,s, payload): 
        s.sendall(payload.encode())
        
        response = bytes("".encode())
        while True:
            data = bytes("".encode())
            data = s.recv(0x4000)
            response = response + data
            try:
                response_as_json = json.loads(response.decode('utf-8'))
                break 
            except:
                pass
            response_as_json = json.loads(response.decode('utf-8'))
            try:
                return response_as_json['result']
            except:
                return 0
            
    def get_parameter(self, ip, jrpc_port):
        #ip = self.ip_address_lineedit.text()
        #jrpc_port = int(self.jrpc_lineedit.text())
        brahma_authenticate = '{"method": "authenticate", "params": {"username": "admin", \
                                "password": "Admin1234"}, "jsonrpc": "2.0", "id": 1}'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, jrpc_port))
        s.sendall(brahma_authenticate.encode())
        response = s.recv(0x4000)
        response_as_json = json.loads(response.decode('utf-8'))

        payload = '{"method": "environment.getcontrolblocks", \
                    "params": {"type": "Sensor", "valuetype": "Temperature"}, \
                    "jsonrpc": "2.0", "id": 2}'
    
        receive_data = self.send_and_receive(s, payload) 
        s.close() 

        return receive_data



    def start_plotting(self):
        # Clear any previous data from the plot
        self.x_data.clear()
        self.y_data.clear()
        self.figure.clear()

        # Start the timer for updating the plot
        self.plot_timer.start(self.plot_interval)

    def stop_plotting(self):
        # Stop the timer for updating the plot
        self.plot_timer.stop()

    def update_plot(self):
        # Generate random data for the plot
        self.x_data.append(len(self.x_data))

        self.y_data = self.get_parameter()


        # Clear the previous plot and create a new one
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.x_data, self.y_data)
        ax.relim()
        ax.autoscale_view()
        self.canvas.draw()

        # Redraw the canvas with the updated plot
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())