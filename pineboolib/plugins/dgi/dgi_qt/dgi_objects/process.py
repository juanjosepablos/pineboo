# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import sys
from typing import Any


class Process(QtCore.QProcess):

    stderr = None
    stdout = None

    def __init__(self, *args) -> None:
        super(Process, self).__init__()
        self.readyReadStandardOutput.connect(self.stdoutReady)
        self.readyReadStandardError.connect(self.stderrReady)
        self.stderr = None
        self.normalExit = self.NormalExit
        self.crashExit = self.CrashExit

        if args:
            self.setProgram(args[0])
            argumentos = args[1:]
            self.setArguments(argumentos)

    def start(self) -> None:
        super(Process, self).start()

    def stop(self) -> None:
        super(Process, self).stop()

    def writeToStdin(self, stdin_) -> None:
        encoding = sys.getfilesystemencoding()
        stdin_as_bytes = stdin_.encode(encoding)
        self.writeData(stdin_as_bytes)
        # self.closeWriteChannel()

    def stdoutReady(self) -> None:
        self.stdout = str(self.readAllStandardOutput())

    def stderrReady(self) -> None:
        self.stderr = str(self.readAllStandardError())

    def readStderr(self) -> Any:
        return self.stderr

    def readStdout(self) -> Any:
        return self.stdout

    def getWorkingDirectory(self) -> Any:
        return super(Process, self).workingDirectory()

    def setWorkingDirectory(self, wd) -> None:
        super(Process, self).setWorkingDirectory(wd)

    def getIsRunning(self) -> bool:
        return self.state() in (self.Running, self.Starting)

    def exitcode(self) -> Any:
        return self.exitCode()

    def executeNoSplit(comando: list, stdin_buffer) -> None:

        list_ = []
        for c in comando:
            list_.append(c)

        pro = QtCore.QProcess()
        programa = list_[0]
        arguments = list_[1:]
        pro.setProgram(programa)
        pro.setArguments(arguments)
        pro.start()
        encoding = sys.getfilesystemencoding()
        stdin_as_bytes = stdin_buffer.encode(encoding)
        pro.writeData(stdin_as_bytes)
        pro.waitForFinished(30000)
        Process.stdout = pro.readAllStandardOutput().data().decode(encoding)
        Process.stderr = pro.readAllStandardError().data().decode(encoding)

    def execute(comando: str) -> None:
        import sys

        encoding = sys.getfilesystemencoding()
        pro = QtCore.QProcess()
        from pineboolib.application import types

        if isinstance(comando, types.Array):
            comando = str(comando)

        if isinstance(comando, str):
            comando = comando.split(" ")

        programa = comando[0]
        argumentos = comando[1:]
        print("**", programa, argumentos)
        pro.setProgram(programa)
        pro.setArguments(argumentos)
        pro.start()
        pro.waitForFinished(30000)
        Process.stdout = pro.readAllStandardOutput().data().decode(encoding)
        Process.stderr = pro.readAllStandardError().data().decode(encoding)

    running = property(getIsRunning)
    workingDirectory = property(getWorkingDirectory, setWorkingDirectory)
