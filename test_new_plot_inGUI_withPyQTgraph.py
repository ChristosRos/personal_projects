import sys 
import os
from PyQt5.QtCore import Qt 
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QDialog
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QComboBox, QFileDialog, QFrame
import csv 
import openpyxl
import pandas as pd 
import plotly.graph_objects as go 
import configparser
import json
import pkg_resources
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg 
import numpy as np

class MainWindow(QWidget):
    def __init__(self):
        super().__init__() 

        self.setWindowTitle("Plotter")
        self.latest1_folder_path = "" 
        self.latest2_folder_path = "" 
        self.folder_path = "" 
        self.file_path = ""
        self.csv_file_path=""
        self.csv_path=""
        self.init_ui()

    def win_stretch(par): 
        for i in range(par.count()):
            par.view().setRowHeight(i, par.fontMetrics().height() + 10) # set row height to fit the text

            item_rect = par.view().visualRect(par.model().index(i, 0)) # get rect for item
            size_hint = par.view().sizeHintForIndex(par.model().index(i, 0)) # get size hint for item
            if item_rect.width() < size_hint.width(): # adjust minimum width if needed
                par.view().setMinimumWidth(size_hint.width() + par.view().verticalScrollBar().sizeHint().width())

    def init_ui(self): 
        self.setGeometry(100,100,1280,768) 
        font = QtGui.QFont('Calibri', 20)

        hbox_tf = QHBoxLayout()
        topframe = QFrame()
        topframe.setFrameShape(QFrame.HLine)
        topframe.setFrameShadow(QFrame.Sunken)
        hbox_tf.addWidget(topframe)


        hbox_bt = QHBoxLayout()
        botframe = QFrame()
        botframe.setFrameShape(QFrame.HLine)
        botframe.setFrameShadow(QFrame.Sunken)
        hbox_bt.addWidget(botframe)


        label = QLabel("Select a .csv file to open:")
        self.label = label
        self.btn_open_folder = QPushButton("Open Folder")
        self.btn_open_folder.clicked.connect(self.open_folder)
        self.combo_box = QComboBox() 
        self.combo_box.view().setMinimumWidth(self.combo_box.width())
       

        label_json = QLabel("Select a json file to open:")
        self.label_json = label_json
        self.btn_open_json = QPushButton("Open/Convert Snapshots")
        self.btn_open_json.clicked.connect(self.load_json)
        
        

        hbox = QHBoxLayout()
        hbox_file = QHBoxLayout()
        vbox_openfolder = QVBoxLayout()
        vbox_openfolder.addWidget(self.btn_open_folder)
        hbox_file.addWidget(label)
        hbox_file.addWidget(self.combo_box)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vbox_openfolder.addLayout(hbox_file)
        hbox.addLayout(vbox_openfolder)
        #hbox.addWidget(label)
        #hbox.addWidget(self.combo_box)
        

        hbox_json = QHBoxLayout()
        hbox_json.addWidget(self.label_json)
        hbox_json.addWidget(self.btn_open_json)
        label_json.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hbox.addLayout(hbox_json)
        

        xaxis_label = QLabel("X-axis Parameter")
        self.xaxis_label = xaxis_label
        yaxis_label = QLabel("Y-axis Parameter")
        self.yaxis_label = yaxis_label
        self.column_combo_box = QComboBox() 
        self.column_combo_box2 = QComboBox()
        self.column_combo_box.view().setMinimumWidth(self.column_combo_box.width())
        self.column_combo_box2.view().setMinimumWidth(self.column_combo_box2.width())

        yaxis_comp= QLabel("Comparison Parameter (Y axis)")
        self.yaxis_comp = yaxis_comp 
        self.sub_combo_box = QComboBox() 
        self.sub_combo_box.view().setMinimumWidth(self.sub_combo_box.width())
        self.plot_button = QPushButton("Plot", self) 
        self.plot_button.clicked.connect(self.plot)
        self.subtract_button = QPushButton("Comparison Plot", self) 
        self.subtract_button.clicked.connect(self.subtract)


        hbox_pars = QHBoxLayout()
        hbox_pars.addWidget(self.xaxis_label)
        hbox_pars.addWidget(self.column_combo_box)
        hbox_pars.addStretch()
        hbox_pars.addWidget(self.yaxis_label)
        hbox_pars.addWidget(self.column_combo_box2)
        hbox_pars.addStretch()
        xaxis_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        yaxis_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        

        sub_but = QHBoxLayout()
        sub_but.addWidget(self.yaxis_comp)
        sub_but.addWidget(self.sub_combo_box)
        yaxis_comp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sub_but.addStretch()

        pl_but = QHBoxLayout()
        pl_but.addWidget(self.plot_button)
        pl_but.addWidget(self.subtract_button)
        pl_but.addStretch()

        #create the layout
        hbox_exit = QHBoxLayout()
        hbox_exit.addStretch() 
        self.exit_button = QPushButton("Exit")
        hbox_exit.addWidget(self.exit_button)
        hbox_exit.addStretch()
        self.exit_button.clicked.connect(self.close)

        ## create a graph window box
        self.graphWidget = pg.PlotWidget() 
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y = True)
        pwg_box = QHBoxLayout() 
        pwg_box.addWidget(self.graphWidget) 


        vbox = QVBoxLayout()
        vbox.addLayout(hbox_tf)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox_bt)
        #vbox.addLayout(hbox_json)
        vbox.addLayout(hbox_pars)
        vbox.addLayout(sub_but)
        vbox.addLayout(pl_but)
        vbox.addLayout(hbox_exit)
        vbox.addLayout(pwg_box)
        
        for i in range(vbox.count()):
            widget = vbox.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setFont(font)

        self.setLayout(vbox)

        #Get the path of the settings.ini file relative to the main executable 
        self.ini_path = pkg_resources.resource_filename(__name__, 'settings.ini')

        #Load the latest folder path from the settings.ini file 
        self.config = configparser.ConfigParser() 
        if os.path.exists(self.ini_path):
            self.config.read(self.ini_path)
        
        self.csv_path = self.config.get('DEFAULT', 'latest2_folder_path', fallback=os.path.expanduser('~'))
        
        self.folder_path = self.config.get('DEFAULT', 'latest1_folder_path', fallback=os.path.expanduser('~'))


    def save_folder_path(self):
        folder_path = self.folder_path
        csv_file_path = os.path.dirname(self.csv_file_path)

        # Update the latest_folder_path value in the settings.ini file 
        if not os.path.exists(self.ini_path):
            self.config['DEFAULT'] = {'latest2_folder_path': csv_file_path}
            self.config['DEFAULT'] = {'latest1_folder_path': folder_path}

        else: 
            if 'DEFAULT' not in self.config:
                self.config['DEFAULT'] = {}
                self.config['DEFAULT']['latest2_folder_path'] = csv_file_path
                
                self.config['DEFAULT'] = {}
                self.config['DEFAULT']['latest1_folder_path'] = folder_path


        with open(self.ini_path, 'w') as configfile:
            self.config.write(configfile)
        csv_file_path = self.csv_path

    def open_folder(self): 
        # Open a folder and populate the dropdown menu with the files inside 
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not folder_path:
            return
        print(f"Selected folder: {folder_path}")
        self.combo_box.clear()
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):# or file_name.endswith(".xlsx"):
                self.combo_box.addItem(file_name)

        #self.combo_box.currentIndexChanged.connect(self.populate_column_names)
        self.combo_box.activated.connect(lambda index: self.populate_column_names(os.path.join(folder_path, self.combo_box.currentText())))
        self.folder_path = folder_path
        self.save_folder_path()


    def clearlayout(self): 
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clearlayout()

    def load_json(self):
        def convert(file1, file2):
            with open(file1) as f: 
                data = json.load(f)
            f.close()
            df = pd.DataFrame() 

            for snapshot in data['snapshots']:
                _df = pd.json_normalize(snapshot)
                _df['timestamp'] = _df['timestamp'].apply(lambda x: pd.to_datetime(x))
                df = pd.concat([df, _df], axis=0, ignore_index=False)
            df = df.set_index("timestamp").apply(lambda x: pd.to_numeric(x, errors='ignore'))
            return df.to_csv(file2)

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", ".", "JSON Files (*.json);;All Files (*)")
        self.file_path = file_path
        if file_path:
            csv_file_path = self.file_path[:-5] + '.csv'
            self.csv_file_path = csv_file_path
            convert(self.file_path, self.csv_file_path)
            self.populate_column_names(self.csv_file_path)


    def populate_column_names(self, index):
        
        self.clearlayout()
        index = self.combo_box.currentIndex()
        file_name = self.combo_box.itemText(index)
        if self.csv_file_path:
            file_path = self.csv_file_path
        else:
            file_path = os.path.join(self.folder_path, file_name)

        df = pd.read_csv(file_path) #if file_name.endswith(".csv") else pd.read_excel(file_path)
        self.df = df
        column_names = df.columns.tolist()
        self.column_combo_box.clear()
        self.column_combo_box2.clear()
        self.sub_combo_box.clear()
        unwanted_cols = ['Unnamed: 0', 'Unnamed: 0.1', 'nbr_proj']
        only_for_plot = ['Type','Serial Number']
        #comparison_pars = ['environment.temperature.NTC_AMBIENT_OUTSIDE', 'environment.lcb.mainboard.CoolantTemp1','environment.lcb.mainboard.CoolantTemp2']
        for column_name in column_names:
            if column_name not in unwanted_cols:
                parameters = column_name
                self.column_combo_box.addItem(column_name)
                self.column_combo_box2.addItem(column_name)
            #if column_name in comparison_pars:
                self.sub_combo_box.addItem(column_name)


    def subtract(self):
        x_column = self.column_combo_box.currentText()
        column = self.column_combo_box2.currentText()
        comparison = self.sub_combo_box.currentText()
        self.subtracted_data = self.df[column] - self.df[comparison]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = self.df[x_column], 
            y = self.subtracted_data,
            name = ''.join([comparison, " - ",column]),
            mode = "markers",
            #text = self.df['Serial Number'],
            hovertemplate = '<br> X Value: %{x} <br> Y Value: %{y}<extra></extra>'
        ))
        fig.update_layout(
             title = ''.join([' <b>Parameter</b>: ', column, ' <b>Comparison</b> vs ', x_column]),
            xaxis_title = x_column,
            yaxis_title = 'Comparison '+ column
        )
        fig.show()


    def plot(self): 
        self.graphWidget.clear()
        column1 = self.column_combo_box.currentText()
        column2 = self.column_combo_box2.currentText()

        if column1 == "time": 
            x = np.arange(len(self.df[column1]))
            y = np.arange(len(self.df[column2]))

            self.graphWidget.setData(x=self.df[column1].values, y=self.df[column2].values)
            self.graphWidget.setXRange(0, len((self.df[column1]))-1)

            max_ticks = 10  # Maximum number of ticks to display
            step = max(1, int(np.ceil(len(self.df[column1]) / max_ticks)))

            ticks = [(i, str(timestamp)) for i, timestamp in enumerate(self.df[column1][::step])] 
            axis = self.graphWidget.getAxis('bottom')
            axis.setTicks([ticks])
        else:
            self.graphWidget.setData(self.df[column1], self.df[column2])
            
            #axis = self.graphWidget.getAxis('bottom')
    
    #def update_plot(self):
    #    self.graphWidget.clear()
    #    column1 = self.column_combo_box
    #    column2 = self.column_combo_box2
    #    self.graphWidget.setData(self.df[column1], self.df[column2], connect='dots')            
       
        



       
    
        #fig = go.Figure()
        #fig.add_trace(go.Scatter(
        #    x = self.df[column1], 
        #    y = self.df[column2], 
        #    mode="markers", 
        #    name=str(self.df[column2]),
        #    #text = self.df['Serial Number'],
        #    hovertemplate = '<br> X Value: %{x} <br> Y Value: %{y} <extra></extra>'
        #))
        #fig.update_layout(
        #    title = ''.join([' Parameter: ', column2, ' vs ', column1]),
        #    xaxis_title = column1,
        #    yaxis_title = column2
        #)
#
        #fig.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())