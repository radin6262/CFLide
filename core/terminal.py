from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt, QProcess # Import QProcess for executing external commands
from PySide6.QtGui import QTextCursor
import getpass
import platform
import os # Import os for path handling

class TerminalWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminal")
        self.setAcceptRichText(False)
        self.setUndoRedoEnabled(False)
        self.setCursorWidth(2)
        
        # QProcess instance for running external commands (like Python scripts)
        self.process = QProcess(self) 
        self.process.readyReadStandardOutput.connect(self.handleStdout)
        self.process.readyReadStandardError.connect(self.handleStderr)
        self.process.finished.connect(self.handleFinished)

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

        # Check if the process is currently running
        if self.process.state() == QProcess.ProcessState.Running:
            self.append("\nProcess already running. Type 'stop' to terminate.")
            self.insertPrompt()
            return

        output = self.runCommand(command)
        if output:
            self.append(output)
            
        # Only insert a new prompt if runCommand didn't execute an external process
        if not self.process.state() == QProcess.ProcessState.Running:
            self.insertPrompt()


    def runCommand(self, command):
        # Standard Terminal commands
        if command == "help":
            return "Available commands: help, clear, echo <msg>, exit, stop"
        elif command.startswith("echo "):
            return command[5:]
        elif command == "clear":
            self.clear()
            return ""
        elif command == "exit":
            self.setDisabled(True)
            return "Terminal session ended."
        elif command == "stop":
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.terminate()
                return "Process termination requested."
            return "No process is currently running."
        elif command == "":
            return ""
        else:
            return f"{command}: command not found"
        
    # 🆕 NEW FUNCTION: Called by the main IDE app's 'Run Code' button
    def execute_file(self, file_path):
        """
        Executes the given file path using the system's python interpreter.
        """
        if not os.path.exists(file_path):
            self.append(f"\nError: File not found at path: {file_path}")
            self.insertPrompt()
            return
        
        if self.process.state() == QProcess.ProcessState.Running:
            self.append("\nError: A process is already running. Please stop it first.")
            self.insertPrompt()
            return

        # Write execution message to terminal
        self.append(f"\n--- Running: python {os.path.basename(file_path)} ---")
        self.moveCursor(QTextCursor.MoveOperation.End)
        
        # Start the external process (e.g., python file.py)
        # Note: 'python' should be in the system PATH
        self.process.start('python', [file_path])


    # 🆕 NEW FUNCTION: Handle output from the external process (stdout)
    def handleStdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.insertPlainText(data)
        self.ensureCursorVisible()

    # 🆕 NEW FUNCTION: Handle errors from the external process (stderr)
    def handleStderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.insertPlainText(data)
        self.ensureCursorVisible()

    # 🆕 NEW FUNCTION: Handle process completion
    def handleFinished(self, exitCode, exitStatus):
        self.append(f"\n--- Process finished with exit code {exitCode} ---")
        self.insertPrompt()