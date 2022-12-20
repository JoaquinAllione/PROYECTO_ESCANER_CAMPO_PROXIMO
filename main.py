import sys 
from PyQt5.QtWidgets import QMainWindow,QApplication
from UI_proyecto import Ui_MainWindow 
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPlainTextEdit, QVBoxLayout

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from UI_inst_settings import Ui_FrequencySettings 

from gcodeparser import GcodeParser
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from HighLighter import *

from PyQt5.QtWidgets import QMessageBox

import pandas as pd

import instrument_SCPI

import resources_rc

class MiApp(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		# SERIAL PORT #

		self.serialPortData = ""
		self.ui.pushButton_connect.setEnabled(True)
		self.ui.pushButton_disconnect.setEnabled(False)

		self.port = QSerialPort()
		self.baudratesDIC = {
		'1200':1200,
		'2400':2400,
		'4800':4800,
		'9600':9600,
		'19200':19200,
		'38400':38400,
		'57600':57600,
		'115200':115200
		}
        
		self.ui.comboBox_baudrate.addItems(self.baudratesDIC.keys())
		self.ui.comboBox_baudrate.setCurrentText('9600')
		self.update_ports()

		self.ui.pushButton_connect.clicked.connect(self.connect_serial)
		self.ui.pushButton_disconnect.clicked.connect(self.disconnect_serial)
		self.ui.pushButton_refresh_port.clicked.connect(self.update_ports)
		self.port.readyRead.connect(self.dataArrive)
		
		###############

		# G-CODE FILE #

		self.highlighter = SyntaxHighlighter(self.ui.plainTextEdit_CodeView.document())
		self.ui.plainTextEdit_CodeView.setReadOnly(True)
		self.commands = []
		self.ui.pushButton_Open.clicked.connect(self.openFile)
		self.ui.label_state.setText(" ")

		###############

		# MEASUREMENT #

		self.update_instruments_list()
		self.df = pd.DataFrame()
		self.time = 1000
		self.index = 0
		self.InProgress = False
		self.timer = QTimer(self)
		self.ui.pushButton_Start.setEnabled(False)
		self.ui.pushButton_Start.clicked.connect(self.startMeasurement)
		self.ui.pushButton_stop.clicked.connect(self.stopMeasurement)
		self.ui.pushButton_pause.clicked.connect(self.pauseMeasurement)
		#self.ui.pushButton_inst_settings.clicked.connect(self.OpenIstrumentSettings)

		###############

		# TABLA #
		self.ui.pushButton_clean.clicked.connect(self.clearTable)
		self.ui.pushButton_Export.clicked.connect(self.exportData)
		#########

		# AJUSTE DE ALTURA #
		self.z_pos = 0.0
		self.ui.pushButton_go_home.clicked.connect(self.Home)
		self.ui.pushButton_Go.clicked.connect(self.Z_positionament)
		self.ui.lineEdit_Z_position.returnPressed.connect(self.Z_positionament)
		#self.ui.pushButton_Z_Up.clicked.connect(self.Z_MoveUp)
		#self.ui.pushButton_Z_Down.clicked.connect(self.Z_MoveDown)
		###############


# TABLA #

	def clearTable(self):
		while (self.ui.tableWidget.rowCount() > 0):
			self.ui.tableWidget.removeRow(0)

	def exportData(self):
		df = pd.DataFrame()

		nrows = self.ui.tableWidget.rowCount()
		for row in range(0,nrows):
			nueva_fila = { 
				'X': self.ui.tableWidget.item(row, 0).text(), 
				'Y': self.ui.tableWidget.item(row, 1).text(),
				'Z': self.ui.tableWidget.item(row, 2).text(),
				'MK1 - Freq.': self.ui.tableWidget.item(row, 3).text(),
				'MK1 - Amp.': self.ui.tableWidget.item(row, 4).text(),
				'MK2 - Freq.': self.ui.tableWidget.item(row, 5).text(),
				'MK2 - Amp.': self.ui.tableWidget.item(row, 6).text(),
				'MK3 - Freq.': self.ui.tableWidget.item(row, 7).text(),
				'MK3 - Amp.': self.ui.tableWidget.item(row, 8).text(),
				'MK4 - Freq.': self.ui.tableWidget.item(row, 9).text(),
				'MK4 - Amp.': self.ui.tableWidget.item(row, 10).text(),
				'MK5 - Freq.': self.ui.tableWidget.item(row, 11).text(),
				'MK5 - Amp.': self.ui.tableWidget.item(row, 12).text(),
				'MK6 - Freq.': self.ui.tableWidget.item(row, 13).text(),
				'MK6 - Amp.': self.ui.tableWidget.item(row, 14).text()
			}
			df = df.append(nueva_fila, ignore_index=True)
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		file_name, _ = QFileDialog.getSaveFileName(self,"Save File","","Text Files(*.csv)",options = options)
		if file_name:
			df.to_csv(file_name + ".csv", index=False)
		
		msg = """Ready!."""
		QMessageBox.information(self, "Save", msg,QMessageBox.Ok)

			
	
#########

# AJUSTE DE ALTURA #

	def Home(self):
		
		msg = """WATCH OUT! The probe should be removed first!"""
		ret = QMessageBox.warning(self, "WATCH OUT!", msg, QMessageBox.Ok, QMessageBox.Abort)
		if ret == QMessageBox.Ok:
			if self.port.isOpen(): 
				self.send_data2board("G28")
				self.ui.lineEdit_Z_position.setText("0.000")
			else:
				msg = """Connect serial port before."""
				QMessageBox.information(self, "Serial Port", msg,QMessageBox.Ok)

	def Z_positionament(self):
		Z_max = 150
		if self.port.isOpen():
			aux = round(float(self.ui.lineEdit_Z_position.text()),3)
			if (aux >= 0 and aux <= Z_max):
				self.z_pos = aux
				self.send_data2board("G0 Z{}".format(self.z_pos))
		else:
				msg = """Connect serial port before."""
				QMessageBox.information(self, "Serial Port", msg,QMessageBox.Ok)


###############

### INSTRUMENT ###
	
	def OpenIstrumentSettings(self):
		self.wind = QMainWindow()
		self.ui = Ui_FrequencySettings()
		self.ui.setupUi(self.wind)
		self.wind.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.wind.setAttribute(QtCore.Qt.WA_TranslucentBackground)

		self.wind.show()

	def update_instruments_list(self):
		list = instrument_SCPI.get_SCPI_resources()
		self.ui.comboBox_instruments_list.clear()
		self.ui.comboBox_instruments_list.addItems(list)

	def getDataMakers(self):
		markers = instrument_SCPI.get_dataMakers()
		print(markers)
	
	def send_data2instrument(self, data):
		instrument_SCPI.SCPI_sendData(data)

##################

### MEASUREMENT ###

	def stopMeasurement(self):
		pass

	def pauseMeasurement(self):
		pass

	def startMeasurement(self):
		if self.port.isOpen():
			self.send_data2board(self.commands[self.index])
			self.ui.label_state.setText("In process...")
			self.InProgress = True
		else:
			msg = """Connect serial port before."""
			QMessageBox.information(self, "Serial Port", msg,QMessageBox.Ok)

	def dataArrive(self):
		if not self.port.canReadLine(): return
		rx = self.port.readLine()
		if (((rx == b'\x00OK\n') or (rx == b'OK\n')) and (self.InProgress == True)):
			self.timer.singleShot(self.time, self.timerOut)

	def timerOut(self):
		ready = False
		if (True):
			self.gcode_marker(self.index)
			if ((self.index <= len(self.commands)+1)):
				self.ui.progressBar.setValue(int((self.index/len(self.commands))*100))
				self.index = self.index+1

				self.ui.tableWidget.setItem(self.index-1, 3, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 4, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 5, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1, 6, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 7, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 8, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1, 9, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 10, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 11, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1, 12, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 13, QTableWidgetItem("x.xxx"))
				self.ui.tableWidget.setItem(self.index-1 , 14, QTableWidgetItem("x.xxx"))
				'''
				instrID = self.ui.comboBox_instruments_list.currentText()
				instrument_SCPI.set_instrumentID(instrID)
				
				maker1 = instrument_SCPI.get_dataMaker(1)
				maker2 = instrument_SCPI.get_dataMaker(2)
				maker3 = instrument_SCPI.get_dataMaker(3)
				maker4 = instrument_SCPI.get_dataMaker(4)
				maker5 = instrument_SCPI.get_dataMaker(5)
				maker6 = instrument_SCPI.get_dataMaker(6)
				
				print(maker1)
				print(maker2)
				print(maker3)
				print(maker4)
				print(maker5)
				print(maker6)
				
				self.ui.tableWidget.setItem(self.index-1, 3, QTableWidgetItem(maker1[0]))
				self.ui.tableWidget.setItem(self.index-1 , 4, QTableWidgetItem(maker1[1]))
				
				self.ui.tableWidget.setItem(self.index-1 , 5, QTableWidgetItem(maker2[0]))
				self.ui.tableWidget.setItem(self.index-1 , 6, QTableWidgetItem(maker2[1]))

				self.ui.tableWidget.setItem(self.index-1 , 7, QTableWidgetItem(maker3[0]))
				self.ui.tableWidget.setItem(self.index-1 , 8, QTableWidgetItem(maker3[1]))

				self.ui.tableWidget.setItem(self.index-1 , 9, QTableWidgetItem(maker4[0]))
				self.ui.tableWidget.setItem(self.index-1 , 10, QTableWidgetItem(maker4[1]))

				self.ui.tableWidget.setItem(self.index-1 , 11, QTableWidgetItem(maker5[0]))
				self.ui.tableWidget.setItem(self.index-1 , 12, QTableWidgetItem(maker5[1]))

				self.ui.tableWidget.setItem(self.index-1 , 13, QTableWidgetItem(maker6[0]))
				self.ui.tableWidget.setItem(self.index-1 , 14, QTableWidgetItem(maker6[1]))
				self.index = self.index +1
				
				'''

				self.ui.plainTextEdit_CodeView.verticalScrollBar().setValue(self.ui.plainTextEdit_CodeView.verticalScrollBar().pageStep()*int(self.index / self.ui.plainTextEdit_CodeView.verticalScrollBar().pageStep())-1)
				self.ui.tableWidget.verticalScrollBar().setValue(self.ui.tableWidget.verticalScrollBar().pageStep()*int(self.index / self.ui.tableWidget.verticalScrollBar().pageStep())-1)
			
			if(self.index == len(self.commands)):
				self.ui.progressBar.setValue(100)
				msg = """Scan completed!"""
				QMessageBox.information(self, "Ready", msg,QMessageBox.Ok)
				self.ui.label_state.setText("Ready!")
				ready = True

		if not ready:
			self.send_data2board(self.commands[self.index])

###################

### G-CODE FILE READ ###

	def openFile(self):
			file , check = QFileDialog.getOpenFileName(None, "Open File",
													"", "G-code Files (*.gcode);;Text Files (*.txt)")
			com = ""
			
			if check:
				self.clearTable()
				self.ui.plainTextEdit_CodeView.clear()
				self.commands.clear()
				with open(file, 'r') as f:
					gcode = f.read()

				parsed_gcode = GcodeParser(gcode)

				for lines in parsed_gcode.lines:
					g = list(lines.command)
					com = str(g[0])+str(g[1])+" "
					self.x_pos = lines.get_param('X')
					self.y_pos = lines.get_param('Y')
					self.z_pos = lines.get_param('Z')

					if(self.x_pos != None):
						self.x_pos = round(float(self.x_pos),3)
						com += "X" + str(self.x_pos)
						

					if(self.y_pos != None):
						self.y_pos = round(float(self.y_pos),3)
						com += " Y" + str(self.y_pos)
						
					
					if(self.z_pos != None):
						self.z_pos = round(float(self.z_pos),3)
						com += " Z" + str(self.z_pos)
					

					self.commands.append(com)

					rowPosition = self.ui.tableWidget.rowCount()
					self.ui.tableWidget.insertRow(rowPosition)
					self.ui.tableWidget.setItem(rowPosition , 0, QTableWidgetItem(str(self.x_pos)))
					self.ui.tableWidget.setItem(rowPosition , 1, QTableWidgetItem(str(self.y_pos))) 
					self.ui.tableWidget.setItem(rowPosition , 2, QTableWidgetItem(self.ui.lineEdit_Z_position.text()))
					#self.df = self.df.append({'X': str(self.x_pos), 'Y': str(self.y_pos), 'Z': str(self.z_pos)}, ignore_index=True)

				for command in self.commands:
					self.ui.plainTextEdit_CodeView.appendPlainText(command)
			
			self.gcode_marker(self.index)
			
			if len(self.commands) > 0: self.ui.pushButton_Start.setEnabled(True)
			##self.commands[0] = "G28"
			#self.df.to_csv (r'export_dataframe.csv',index = False, header=True)
			self.ui.plainTextEdit_CodeView.verticalScrollBar().setValue(0)
 
    


	def gcode_marker(self, lineNumber):
		fmt = QTextCharFormat()
		fmt.setBackground(QColor(71, 129, 255, 255))
		self.highlighter.clear_highlight()
		self.highlighter.highlight_line(lineNumber, fmt)

########################

### SERIAL PORT FUNTIONS ###

	def update_ports(self):
			self.ui.comboBox_port_list.clear()
			self.ui.comboBox_port_list.addItems([ port.portName() for port in QSerialPortInfo().availablePorts() ])		

	def disconnect_serial(self):
			if self.port.isOpen():
				self.port.close()
				#send msg "DISCONNECTED!"
				self.ui.label_status.setText("Disconnected")
				self.ui.pushButton_disconnect.setEnabled(False)
				self.ui.pushButton_connect.setEnabled(True)

	def connect_serial(self):		
			try:
				port = self.ui.comboBox_port_list.currentText()
				baud = self.ui.comboBox_baudrate.currentText()
				self.port.setBaudRate(int(baud))
				self.port.setPortName(port)
				if self.port.open(QtCore.QIODevice.ReadWrite):
					#send msg "CONNECTED!"
					self.ui.pushButton_disconnect.setEnabled(True)
					self.ui.pushButton_connect.setEnabled(False)
					self.ui.label_status.setText("Connected to " + port)
					msg = """Successful Connection! Connected to {}.""".format(port)
					QMessageBox.information(self, "Serial Port", msg,QMessageBox.Ok)
			except:
				#send msg "ERROR!"
				msg = """Error ocurred"""
				QMessageBox.critical(self, "Serial Port", msg,QMessageBox.Ok)
				pass
			finally:
				pass

	def send_data2board(self, data):
		try:
			if self.port.isOpen():
				data = data + '\n'
				self.port.write(data.encode())
			else:
				#send msg "NOT CONNECTED"
				msg = """Connect serial port before."""
				QMessageBox.information(self, "Serial Port", msg,QMessageBox.Ok)
				pass
		except:
			#send msg "ERROR!"
			msg = """Error ocurred"""
			QMessageBox.critical(self, "Serial Port", msg,QMessageBox.Ok)
			pass
		finally:
			pass

############################

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MiApp()
	w.showMaximized()
	sys.exit(app.exec_())