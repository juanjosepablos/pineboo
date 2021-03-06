"""Flserial por module."""

from PyQt5 import QtCore
from pineboolib.core import decorators
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5 import QtSerialPort  # type: ignore [attr-defined]


class BaudRateType(object):
    """BaudRateType class."""

    BAUD50: int = -1
    BAUD75: int = -1
    BAUD110: int = -1
    BAUD134: int = -1
    BAUD150: int = -1
    BAUD200: int = -1
    BAUD300: int = -1
    BAUD600: int = -1
    BAUD1200: int = 1200
    BAUD1800: int = -1
    BAUD2400: int = 2400
    BAUD4800: int = 4800
    BAUD9600: int = 9600
    BAUD14400: int = -1
    BAUD19200: int = 19200
    BAUD38400: int = 38400
    BAUD56000: int = -1
    BAUD57600: int = 57600
    BAUD76800: int = -1
    BAUD115200: int = 115200
    BAUD128000: int = -1
    BAUD256000: int = -1


class DataBitsType(object):
    """DataBitsType class."""

    DATA_5: int = 5
    DATA_6: int = 6
    DATA_7: int = 7
    DATA_8: int = 8


class ParityType(object):
    """ParityType class."""

    PAR_NONE: int = 0
    PAR_EVEN: int = 2
    PAR_ODD: int = 3
    PAR_SPACE: int = 4
    PAR_MARK: int = 5


class StopBitType(object):
    """StopBitType class."""

    STOP_1: int = 1
    STOP_1_5: int = 3
    STOP_2: int = 2


class FlowType(object):
    """FlowType class."""

    FLOW_OFF: int = 0
    FLOW_HARDWARE: int = 1
    FLOW_XONXOFF: int = 2


class FLSerialPort(QtCore.QObject, BaudRateType, DataBitsType, ParityType, StopBitType, FlowType):
    """FLSerialPort class."""

    _obj: "QtSerialPort.QSerialPort"

    def __init__(self, port_name: str) -> None:
        """Inicialize."""
        super().__init__()
        if str(QtCore.QSysInfo()) == "ios":
            from pineboolib.q3widgets.messagebox import MessageBox

            MessageBox.information(
                None,
                self.tr("Opción deshabilitada"),
                self.tr("FLSerialPort no está disponible para IOS"),
                MessageBox.Ok,
            )
            return
        else:
            from PyQt5 import QtSerialPort  # type: ignore [attr-defined] # noqa: F821

            self._obj = QtSerialPort.QSerialPort(port_name)

    def setBaudRate(self, baud_rate: int) -> None:
        """Set baud rate."""
        self._obj.setBaudRate(baud_rate)

    def baudRate(self) -> int:
        """Return actual baud rate."""
        return self._obj.baudRate()

    def setDataBits(self, data_bits: int) -> None:
        """Set data bits."""
        self._obj.setDataBits(data_bits)

    def dataBits(self) -> int:
        """Return actual data bits."""
        return self._obj.dataBits()

    def setParity(self, parity: int) -> None:
        """Set parity check value."""
        self._obj.setParity(parity)

    def parity(self) -> int:
        """Return parity check."""
        return self._obj.parity()

    def setStopBits(self, stop_bit: int) -> None:
        """Set stop bits."""
        self._obj.setStopBits(stop_bit)

    def stopBits(self) -> int:
        """Return stop bits."""
        return self._obj.stopBits()

    def setFlowControl(self, flow: int) -> None:
        """Set flow conrol."""
        self._obj.setFlowControl(flow)

    def flowControl(self) -> int:
        """Return flow control."""
        return self._obj.flowControl()

    def setTimeOut(self, sec: int = 0, milisec: int = 3000) -> None:
        """Set time out."""
        time = milisec
        if sec:
            time = sec * 1000 + time

        self._obj.waitForBytesWritten(time)
        self._obj.waitForReadyRead(time)

    def open(self) -> bool:
        """Return if port is open."""
        return self._obj.open()

    def close(self) -> bool:
        """Return if port is closed."""
        return self._obj.close()

    @decorators.NotImplementedWarn
    def writeText(self, data: str) -> None:
        """Send string data."""
        pass

    @decorators.NotImplementedWarn
    def getch(self) -> int:
        """Return int char readed from port."""
        return 0

    @decorators.NotImplementedWarn
    def putch(self, ch: int) -> int:
        """Send a char."""
        return 0

    @decorators.NotImplementedWarn
    def ungetch(self, ch: int) -> int:
        """Return unsigned char?."""
        return 0

    def size(self) -> int:
        """Return size data recceived."""
        return self._obj.size()

    def flush(self) -> bool:
        """Flush data."""
        return self._obj.flush()

    @decorators.NotImplementedWarn
    def readBlock(self) -> int:
        """Read data block."""
        return 0

    def writeBlock(self) -> int:
        """Write data block."""
        return 0

    def bytesAvailable(self) -> int:
        """Return number of bytes avalaible to read."""
        return 0

    def setRts(self, b: bool) -> None:
        """Emit RTS. signal."""
        self._obj.setRequestToSend(b)

    def setDtr(self, b: bool) -> None:
        """Emit DTR signal."""
        self._obj.setDataTerminalReady(b)
