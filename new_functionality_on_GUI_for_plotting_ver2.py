from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QHeaderView, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QComboBox, QFileDialog, QPushButton, QTableWidget, QTableWidgetItem
import pandas as pd
import sys
import plotly.graph_objects as go


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Plotter")
        self.csv_data = None
        self.selected_parameters = []
        self.selected_category = None 
        self.selected_parameter = None
        self.category_selected = False

        self.init_ui()

    def init_ui(self):
        # Layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        # Drag and drop label
        drop_label = QLabel("Drag and drop a CSV file here:")
        drop_label.setAlignment(QtCore.Qt.AlignCenter)
        drop_label.setStyleSheet("border: 2px dashed #ccc;")
        drop_label.setAcceptDrops(True)
        drop_label.installEventFilter(self)
        drop_label.dragEnterEvent = self.drag_enter_event
        drop_label.dropEvent = self.drop_event
        hbox.addWidget(drop_label)

        # Parameter selection based on category 
        self.category_combo = QComboBox(self)
        #self.category_combo.setEnabled(False)
        self.category_combo.currentIndexChanged.connect(self.update_filtered_parameters) 
        self.parameter_combo = QComboBox(self)
        self.parameter_combo.currentIndexChanged.connect(self.add_to_the_table)
        hbox.addWidget(self.category_combo)
        hbox.addWidget(self.parameter_combo)

        

        # Plot button
        plot_button = QPushButton("Plot", self)
        plot_button.clicked.connect(self.plot)
        hbox.addWidget(plot_button)

        # Parameter table
        self.parameter_table = QTableWidget(self)
        self.parameter_table.setColumnCount(2)
        self.parameter_table.setHorizontalHeaderLabels(["Parameter", "Action"])
        self.parameter_table.horizontalHeader().setStretchLastSection(True)
        self.parameter_table.setColumnWidth(0, 500)  # Parameter column width
        self.parameter_table.setColumnWidth(1, 100)
        vbox.addLayout(hbox)
        vbox.addWidget(self.parameter_table)

        self.setLayout(vbox)
        self.setGeometry(100, 100, 800, 600)

    def drag_enter_event(self, event): 
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event): 
        if event.mimeData().hasUrls(): 
            file_url = event.mimeData().urls()[0]
            file_path = file_url.toLocalFile()

            try: 
                self.load_csv(file_path)
                event.acceptProposedAction()
            except Exception as e:
                print("Error loading CSV:", e)


    def load_csv(self, file_path):
        try:
            self.csv_data = pd.read_csv(file_path)
            self.parameter_names = list(self.csv_data.columns)
            self.add_selected_category()
        except Exception as e:
            print(f"Error loading CSV file: {e}")



    def add_selected_category(self):
        categories = ["TEC","fcb","ldm","mainboard","peltierboard","temperature","liquidpressure"]
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        #self.category_selected = True
        
        #self.category_combo.currentIndexChanged.connect(self.update_filtered_parameters)

    def update_filtered_parameters(self,index):
        self.selected_category = self.category_combo.itemText(index)
        self.parameter_combo.clear()

        if self.csv_data is None or self.selected_category is None:
            return

        filtered_parameters = [name for name in self.parameter_names if self.selected_category in name]
        self.parameter_combo.addItems(filtered_parameters)
        #self.parameter_combo.clear()
#
    def add_to_the_table(self):
        parameter_combo = self.sender()
        self.selected_parameter = parameter_combo.currentText()

        if self.selected_parameter and self.selected_parameter not in self.selected_parameters:
            
            self.selected_parameters.append(self.selected_parameter)

            # Add the parameter to the table
            row_count = self.parameter_table.rowCount()
            self.parameter_table.insertRow(row_count)

            parameter_item = QTableWidgetItem(self.selected_parameter)
            parameter_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.parameter_table.setItem(row_count, 0, parameter_item)

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(self.remove_parameter)
            self.parameter_table.setCellWidget(row_count, 1, remove_button)

    def remove_parameter(self):
        button = self.sender()
        row = self.parameter_table.indexAt(button.pos()).row()

        parameter = self.parameter_table.item(row, 0).text()
        self.selected_parameters.remove(parameter)

        self.parameter_table.removeRow(row)

    def plot(self):
        if not self.selected_parameters:
            return

        fig = go.Figure()

        for parameter in self.selected_parameters:
            fig.add_trace(go.Scatter(x=self.csv_data['time'], y=self.csv_data[parameter], mode='markers', name=parameter))

        fig.show()
#    def add_selected_category(self): 
#        categories = ["TEC","fcb","ldm","mainboard","peltierboard","temperature","liquidpressure"]
#        self.category_combo.clear()
#        self.category_combo.addItems(categories)
#        self.category_combo.currentIndexChanged.connect(self.update_parameter_combo)
#      
#    def update_parameter_combo(self, index): 
#        self.add_selected_category = self.category_combo.currentText() 
#        self.update_filtered_parameters()
#    
#    def update_filtered_parameters(self):
#        #selected_category = self.category_combo.currentText()
#        self.parameter_combo.clear()
#
#        if self.selected_category:
#            filtered_parameter = [name for name in self.parameter_names if self.selected_category in name]
#            self.parameter_combo.addItems(filtered_parameter)
#    
#    def add_to_the_table(self,index):
#        parameter_combo = self.sender()
#        self.selected_parameter = parameter_combo.currentText()
#        
#        #if parameter != "Select Parameter" and parameter not in self.selected_parameters:
#        if self.selected_parameter and self.selected_parameter not in self.selected_parameters:
#            self.selected_parameters.append(self.selected_parameter)
#
#            # Add the parameter to the table
#            row_count = self.parameter_table.rowCount()
#            self.parameter_table.insertRow(row_count)
#
#            parameter_item = QTableWidgetItem(self.selected_parameter)
#            parameter_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
#            self.parameter_table.setItem(row_count, 0, parameter_item)
#
#            remove_button = QPushButton("Remove")
#            remove_button.clicked.connect(self.remove_parameter)
#            self.parameter_table.setCellWidget(row_count, 1, remove_button)
#
#            # Set the size of the first row to stretch
#            self.parameter_table.resizeColumnsToContents()
#
#    def remove_parameter(self):
#        button = self.sender()
#        row = self.parameter_table.indexAt(button.pos()).row()
#
#        parameter = self.parameter_table.item(row, 0).text()
#        self.selected_parameters.remove(parameter)
#
#        self.parameter_table.removeRow(row)
#
#
#
#
#    def plot(self):
#        if not self.selected_parameters:
#            return
#
#        fig = go.Figure()
#
#        for parameter in self.selected_parameters:
#            fig.add_trace(go.Scatter(x=self.csv_data['time'], y=self.csv_data[parameter], mode='markers',name=parameter))
#
#        fig.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        



    
