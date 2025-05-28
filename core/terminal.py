from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
import getpass
import platform
from PySide6.QtGui import QTextCursor


class TerminalWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminal")
        self.setAcceptRichText(False)
        self.setUndoRedoEnabled(False)
        self.setCursorWidth(2)

        self.username = getpass.getuser()
        self.hostname = platform.node()
        self.prompt = f"{self.username}@{self.hostname}:~$ "
        self.insertPrompt()

    def insertPrompt(self):
        self.append(self.prompt)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def keyPressEvent(self, event):
        # Only allow editing after prompt
        cursor = self.textCursor()
        prompt_pos = cursor.block().position() + len(self.prompt)

        if event.key() == Qt.Key_Backspace:
            if cursor.position() > prompt_pos:
                super().keyPressEvent(event)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.processCommand()
        else:
            super().keyPressEvent(event)

    def processCommand(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
        line = cursor.selectedText()
        command = line[len(self.prompt):].strip()

        output = self.runCommand(command)
        if output:
            self.append(output)
        self.insertPrompt()


    def runCommand(self, command):
        if command == "help":
            return "Available commands: help, clear, echo <msg>, exit"
        elif command.startswith("echo "):
            return command[5:]
        elif command == "clear":
            self.clear()
            return ""
        elif command == "exit":
            self.setDisabled(True)
            return "Terminal session ended."
        elif command == "":
            return ""
        else:
            return f"{command}: command not found"
