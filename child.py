from PyQt5.QtWidgets import *
import sys
 
class Main(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle(" ")
    button = QPushButton(" ", self)
    button.clicked.connect(self.show_child)
 
  def show_child(self):
    self.child_window = Child()
    self.child_window.show()
 
class Child(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle(" ")
 
#  
if __name__ == "__main__":
  app = QApplication(sys.argv)
 
  window = Main()
  window.show()
 
  sys.exit(app.exec_())