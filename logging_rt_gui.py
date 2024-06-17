import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QLabel, QLineEdit, QHBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import socket
import json
import time
from time import sleep


class WorkerThread(QThread):
    dataReady = pyqtSignal(object)

    def __init__(self, ip, jrpc_port, duration, authenticate_payload):
        super().__init__()
        self.ip = ip
        self.jrpc_port = jrpc_port
        self.duration = duration
        self.interval = 0.1
        #self.authenticate_payload = '{"method": "authenticate", "params": {"username": "admin", \
        #                        "password": "Admin1234"}, "jsonrpc": "2.0", "id": 1}'
        self.authenticate_payload = authenticate_payload

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.jrpc_port))
        s.sendall(self.authenticate_payload.encode())
        response = s.recv(0x4000)
        response_as_json = json.loads(response.decode('utf-8'))

        payload ='{"method": "environment.getcontrolblocks", \
                    "params": {"type": "Sensor", "valuetype": "Speed"}, \
                    "jsonrpc": "2.0", "id": 3}'
        tstart =time.time() 
        while time.time() - tstart < float(self.duration) * 60:
            data_raw = self.get_parameter(s, payload)
            string = "environment.fanspeed.FAN13"
            #data = {k: v for k, v in data_raw.items() if any(substring in k for substring in string)}
            data = {k: v for k, v in data_raw.items() if  string in k}
            self.dataReady.emit(data)
            sleep(self.interval)

        s.close()

    def get_parameter(self, s, payload):
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


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Plot App")
        self.setGeometry(100, 100, 600, 400)


        self.ip_address_label = QLabel("IP Address:") 
        self.ip_address_lineedit = QLineEdit() 
        self.jrpc_label = QLabel("JRPC port:")
        self.jrpc_lineedit = QLineEdit()
        self.duration_label = QLabel("Duration(mins):")
        self.duration_box = QLineEdit()
        self.startButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")
        self.canvas = PlotCanvas()

        # Set up Layout
        layout = QVBoxLayout()
        hbox = QHBoxLayout() 
        hbox.addWidget(self.ip_address_label)
        hbox.addWidget(self.ip_address_lineedit)
        hbox.addWidget(self.jrpc_label)
        hbox.addWidget(self.jrpc_lineedit)
        hbox.addWidget(self.duration_label)
        hbox.addWidget(self.duration_box)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.startButton)
        hbox2.addWidget(self.stopButton)
        layout.addLayout(hbox)
        layout.addLayout(hbox2)
        layout.addWidget(self.canvas)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.startButton.clicked.connect(self.start_plotting)
        self.stopButton.clicked.connect(self.stop_plotting)

        self.thread = None
       

    def start_plotting(self):
        ip = self.ip_address_lineedit.text()
        duration = self.duration_box.text()
        JRPC_port = int(self.jrpc_lineedit.text())  # Replace with the actual port
        authenticate_payload = '{"method": "authenticate", "params": {"username": "admin", \
                                "password": "Admin1234"}, "jsonrpc": "2.0", "id": 1}'  # Replace with the actual payload

        self.thread = WorkerThread(ip, JRPC_port, duration, authenticate_payload)
        self.thread.dataReady.connect(self.update_plot)
        self.thread.start()

    def stop_plotting(self):
        if self.thread is not None:
            self.thread.terminate()
            self.thread.wait()
            self.thread = None

    def update_plot(self, data): 
        self.canvas.update_plot(data)

class PlotCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure() 
        super().__init__(self.fig) 
        self.ax = self.fig.add_subplot(111)
        self.lines = {} 

    def update_plot(self, data): 
        self.ax.clear()
        self.ax.legend(loc="upper left")
        x_data = []
        y_data = {} 

        for key,value in data.items():
            if key not in self.lines:
                self.lines[key], = self.ax.plot([], [], "-o", label=key)
                y_data[key] = []
            else:
                y_data[key] = self.lines[key].get_ydata()

            y_data[key].append(value)
            self.lines[key].set_ydata(y_data[key])

            x_data = list(range(len(y_data[key])))
            self.lines[key].set_data(x_data, y_data[key])

        for line in self.lines.values(): 
            self.ax.plot(x_data, line.get_ydata(), "-o")

        self.ax.legend()
        #self.ax.plot(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())
