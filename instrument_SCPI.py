import pyvisa
from PyQt5.QtWidgets import QMessageBox

instID = ""

def set_instrumentID(instrumentId: str) -> None:
    global instID
    instID = instrumentId

def set_freqCenter(freqCenter: int) -> None:
    SCPI_sendData('FREQ:CENT ' + str(freqCenter))

def set_freqStep(freqStep: int) -> None:
    SCPI_sendData('FREQ:STEP ' + str(freqStep))

def set_freqStart(freqStart: int) -> None:
    SCPI_sendData('FREQ:START ' + str(freqStart))

def set_freqStop(freqStop: int) -> None:
    SCPI_sendData('FREQ:STOP ' + str(freqStop))

def get_freqCenter() -> float:
    return((SCPI_sendData('FREQ:CENT?')))

def get_freqStep() -> float:
    return((SCPI_sendData('FREQ:STEP?')))

def get_freqStart() -> float:
    return((SCPI_sendData('FREQ:START?')))

def get_freqStop() -> float:
    return((SCPI_sendData('FREQ:STOP?')))

def get_instrumentID() -> str:
    return((SCPI_sendData('*IDN?')))

def SCPI_sendData(data: str): #Envia instrucciones al instrumento al cual referencia instrumentId
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(instID)
        result = None
        if(data.count("?") > 0):
            result = inst.query(data)
            return result
        else:
            inst.write(data)
        inst.close()

    except:
        msg = """Se ha producido un error!."""
        QMessageBox.critical("Error", msg,QMessageBox.Ok)

def get_dataMakers2()-> list:
	markers_info = []
	cant_makers = 6
	
	for i in range(1, cant_makers+1):
		#SCPI_sendData("CALC:MARK{} ON".format(i))
		#SCPI_sendData("CALC:MARK{}:MAX".format(i))
		marker_i = (SCPI_sendData("CALC:MARK{}:X?".format(i)), SCPI_sendData("CALC:MARK{}:Y?".format(i)))
		markers_info.append(marker_i)

	return markers_info

def get_dataMaker(mark: int)-> list:
	
	#marker = [SCPI_sendData("CALC:MARK{}}:X?".format(mark)), SCPI_sendData("CALC:MARK{}}:Y?".format(mark))]
    marker = [SCPI_sendData(":CHANnel1:AMPLitude:UNIT?"), 'holis']
    return marker
		
def get_SCPI_resources() -> list:
	rm = pyvisa.ResourceManager()
	resources = rm.list_resources()
	return resources

