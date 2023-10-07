from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import mysql.connector
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datapresentdesign import Ui_MainWindow


class DataPresentationApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.database_command_button_2.accepted.connect(self.handle_database_command)
        self.ui.table_command_button.clicked.connect(self.handle_table_command)
        self.ui.presentation_button.clicked.connect(self.presentation_button)

    def plot_line_chart(self, x_data, y_data, column_a, column_b):
        figure = Figure()
        ax = figure.add_subplot(111)
        ax.plot(x_data, y_data)
        ax.set_xlabel(column_a)
        ax.set_ylabel(column_b)
        ax.set_title('Line Chart')

        canvas = FigureCanvas(figure)
        self.ui.chat_graphicView.setScene(QtWidgets.QGraphicsScene(self))
        self.ui.chat_graphicView.setSceneRect(0, 0, 800, 600)
        self.ui.chat_graphicView.setSceneItem(canvas)
        canvas.draw()

        def plot_pie_chart(self, labels, sizes):
            try:
                figure = Figure()
                ax = figure.add_subplot(111)
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title('Pie Chart')

                canvas = FigureCanvas(figure)
                self.ui.pie_graphicview.setScene(QtWidgets.QGraphicsScene(self))
                self.ui.pie_graphicview.setSceneRect(0, 0, 800, 600)
                self.ui.pie_graphicview.setSceneItem(canvas)
                canvas.draw()

            except Exception as e:
                self.show_alert("Error plotting pie chart: " + str(e))

    def plot_bar_chart(self, x_data, y_data, column_a, column_b):
        figure = Figure()
        ax = figure.add_subplot(111)
        ax.bar(x_data, y_data)
        ax.set_xlabel(column_a)
        ax.set_ylabel(column_b)
        ax.set_title('Bar Chart')

        canvas = FigureCanvas(figure)
        self.ui.bar_graphicView.setScene(QtWidgets.QGraphicsScene(self))
        self.ui.bar_graphicView.setSceneRect(0, 0, 800, 600)
        self.ui.bar_graphicView.setSceneItem(canvas)
        canvas.draw()

    def handle_database_command(self):
        database = self.ui.database_line_edit.text()
        server = self.ui.server_line_edit.text()
        username = self.ui.username_line_edit.text()
        password = self.ui.password_line_edit.text()

        if not all([database, server, username]):
            self.show_alert("Please fill in the required fields.")
            return

        try:
            # Establish a database connection using mysql-connector-python
            conn = mysql.connector.connect(
                host=server,
                user=username,
                password=password,
                database=database
            )

            # Check if the connection is successful
            if conn.is_connected():
                self.show_alert("Connected to the database.")

                # Fetch table names and populate the table combo box
                try:
                    tables = self.fetch_table_names(conn)
                    self.populate_combo_box(self.ui.tables_comboBox, tables)
                except Exception as e:
                    self.show_alert("Error fetching table names: " + str(e))

                conn.close()  # Close the connection after displaying the message
            else:
                self.show_alert("Unable to connect to the database.")
                return
        except mysql.connector.Error as e:
            self.show_alert("Error: Unable to connect to the database - " + str(e))

    def handle_table_command(self):
        selected_table = self.ui.tables_comboBox.currentText()
        if selected_table == "Select Table Name":
            self.show_alert("Please Select Table Name.")
            return

        # Fetch column names for the selected table and populate combo boxes
        try:
            columns = self.fetch_column_names(selected_table)
            self.populate_combo_box(self.ui.column_comboBoxA, columns)
            self.populate_combo_box(self.ui.column_comboBoxB, columns)

            # Automatically select the first column for column A and B
            if len(columns) > 1:
                self.ui.column_comboBoxA.setCurrentIndex(1)
                self.ui.column_comboBoxB.setCurrentIndex(2)

        except Exception as e:
            self.show_alert("Error fetching column names: " + str(e))

    def fetch_table_names(self, conn):
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return tables

    def fetch_column_names(self, table_name):
        conn = mysql.connector.connect(
            host=self.ui.server_line_edit.text(),
            user=self.ui.username_line_edit.text(),
            password=self.ui.password_line_edit.text(),
            database=self.ui.database_line_edit.text()
        )
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        cursor.close()
        conn.close()
        return columns

    def populate_combo_box(self, combo_box, items):
        combo_box.clear()
        combo_box.addItem("Select Data name")
        for item in items:
            combo_box.addItem(item)

    def show_alert(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Alert")
        msg_box.setText(message)
        msg_box.exec_()

    def fetch_data_from_database(self, selected_column_a, selected_column_b):
        if self.selected_table is None:
            self.show_alert("Please select a table.")
            return

        try:
            conn = mysql.connector.connect(
                host=self.ui.server_line_edit.text(),
                user=self.ui.username_line_edit.text(),
                password=self.ui.password_line_edit.text(),
                database=self.ui.database_line_edit.text()
            )

            cursor = conn.cursor()
            cursor.execute(f"SELECT {selected_column_a}, {selected_column_b} FROM {self.selected_table}")
            result = cursor.fetchall()
            conn.close()

            x_data = [row[0] for row in result]
            y_data = [row[1] for row in result]

            return x_data, y_data

        except mysql.connector.Error as e:
            self.show_alert("Error: Unable to fetch data from the database - " + str(e))

    def handle_table_command(self):
        self.selected_table = self.ui.tables_comboBox.currentText()
        if self.selected_table == "Select Table Name":
            self.show_alert("Please Select Table Name.")
            return

        # Fetch column names for the selected table and populate combo boxes
        try:
            columns = self.fetch_column_names(self.selected_table)
            self.populate_combo_box(self.ui.column_comboBoxA, columns)
            self.populate_combo_box(self.ui.column_comboBoxB, columns)

            # Automatically select the first column for column A and B
            if len(columns) > 1:
                self.ui.column_comboBoxA.setCurrentIndex(1)
                self.ui.column_comboBoxB.setCurrentIndex(2)

        except Exception as e:
            self.show_alert("Error fetching column names: " + str(e))
##This is the place i need to fix..
    def presentation_button(self):
        selected_column_a = self.ui.column_comboBoxA.currentText()
        selected_column_b = self.ui.column_comboBoxB.currentText()

        if selected_column_a == "Select Data name" or selected_column_b == "Select Data name":
            self.show_alert("Please select valid columns.")
            return

        # Fetch data from the database
        data = self.fetch_data_from_database(selected_column_a, selected_column_b)

        if data is not None:
            x_data, y_data = data
            selected_graphic_view = self.ui.VIEWS.currentIndex()

            if selected_graphic_view == 0:  # Line chart
                self.plot_line_chart(x_data, y_data, selected_column_a, selected_column_b)
            elif selected_graphic_view == 1:  # Bar chart
                self.plot_bar_chart(x_data, y_data, selected_column_a, selected_column_b)
            elif selected_graphic_view == 2:  # Pie chart
                # Sample data for pie chart (replace with your own data)
                labels = ['Category A', 'Category B', 'Category C']
                sizes = [30, 45, 25]
                self.plot_pie_chart(labels, sizes)  # Pass sample data for pie chart
        else:
            self.show_alert("Error fetching data from the database.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = DataPresentationApp()
    MainWindow.show()
    sys.exit(app.exec_())
