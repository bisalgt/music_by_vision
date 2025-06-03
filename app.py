import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QGridLayout



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label_stream = QLabel(self)
        self.pixmap = QPixmap("./output/concept_gui_app.png")
        self.label_stream.setPixmap(self.pixmap)
        

        self.btn = QPushButton("Button")
    
        layout = QGridLayout()
        layout.addWidget(self.label_stream, 0,0)
        layout.addWidget(self.btn, 1,0)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()