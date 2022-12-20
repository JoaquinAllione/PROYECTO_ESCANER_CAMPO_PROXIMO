import sys 
from PyQt5.QtWidgets import QMainWindow,QApplication
from UI_inst_settings import Ui_FrequencySettings 
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QMessageBox

import instrument_SCPI

from PyQt5 import QtCore

import resources_rc

class MiApp(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_FrequencySettings()
		self.ui.setupUi(self)
		self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		
		self.update_instruments_list()
		
		self.ui.pushButton_close.clicked.connect(self.closeWindow)
		self.ui.pushButton_SendSettings.clicked.connect(self.sendSettings)
		self.ui.pushButton_CheckSettings.clicked.connect(self.checkSettings)

        

	def update_instruments_list(self):
		list = instrument_SCPI.get_SCPI_resources()
		self.ui.comboBox_instruments_list.clear()
		self.ui.comboBox_instruments_list.addItems(list)

	def sendSettings(self):

		instrID = self.ui.comboBox_instruments_list.currentText()
		instrument_SCPI.set_instrumentID(instrID)

		instrument_SCPI.set_freqCenter(self.ui.doubleSpinBox_FreqCenter.value())
		instrument_SCPI.set_freqStep(self.ui.doubleSpinBox_FreqStep.value())
		instrument_SCPI.set_freqStart(self.ui.doubleSpinBox_FreqStart.value())
		instrument_SCPI.set_freqStop(self.ui.doubleSpinBox_FreqStop.value())

		msg = "Configuracion exitosa!"
		QMessageBox.information(self, "Instrument setting", msg,QMessageBox.Ok)

	def checkSettings(self):
		
		instrID = self.ui.comboBox_instruments_list.currentText()
		instrument_SCPI.set_instrumentID(instrID)

		instName = instrument_SCPI.get_instrumentID()
		
		print(instName)

		makers = instrument_SCPI.get_dataMakers()
		print(makers)
	
		#self.ui.doubleSpinBox_FreqCenter.setValue(float(instrument_SCPI.get_freqCenter()))

		

	def closeWindow(self):
		self.close()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MiApp()
	w.show()
	sys.exit(app.exec_())