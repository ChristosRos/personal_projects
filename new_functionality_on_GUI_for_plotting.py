from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QComboBox, QFileDialog, QPushButton, QTableWidget, QTableWidgetItem
import pandas as pd
import sys
import plotly.graph_objects as go


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Plotter")
        self.csv_data = None
        self.selected_parameters = []

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

        # Parameter selection
        self.parameter_combo = QComboBox()
        self.parameter_combo.currentIndexChanged.connect(self.add_selected_parameter)
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


        #self.parameter_table = QTableWidget()
        #self.parameter_table.setColumnCount(1)
        #self.parameter_table.setHorizontalHeaderLabels(["Projector Parameters"])
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

    #def eventFilter(self, source, event):
    #    if (event.type() == QtCore.QEvent.DragEnter and source is self) or (
    #        event.type() == QtCore.QEvent.Drop and source is self
    #    ):
    #        event.accept()
    #        return True
    #    elif event.type() == QtCore.QEvent.Drop:
    #        urls = event.mimeData().urls()
    #        if urls:
    #            file_path = urls[0].toLocalFile()
    #            self.load_csv(file_path)
    #        return True
#
    #    return super().eventFilter(source, event)

    def load_csv(self, file_path):
        try:
            self.csv_data = pd.read_csv(file_path)
            self.parameter_combo.clear()
            self.parameter_combo.addItems(self.csv_data.columns)
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    #def add_selected_parameter(self, index):
    #    parameter = self.parameter_combo.currentText()
    #    if parameter not in self.selected_parameters:
    #        self.selected_parameters.append(parameter)
    #        self.update_parameter_table()
#
    #def update_parameter_table(self):
    #    self.parameter_table.setRowCount(len(self.selected_parameters))
    #    for i, parameter in enumerate(self.selected_parameters):
    #        item = QTableWidgetItem(parameter)
    #        self.parameter_table.setItem(i, 0, item)

    
    def add_selected_parameter(self, index):
        parameter_combo = self.sender()
        parameter = parameter_combo.currentText()

        if parameter != "Select Parameter" and parameter not in self.selected_parameters:
            self.selected_parameters.append(parameter)

            # Add the parameter to the table
            row_count = self.parameter_table.rowCount()
            self.parameter_table.insertRow(row_count)

            parameter_item = QTableWidgetItem(parameter)
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
            fig.add_trace(go.Scatter(x=self.csv_data.index, y=self.csv_data[parameter], name=parameter))

        fig.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        



    
