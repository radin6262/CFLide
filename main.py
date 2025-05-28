from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QToolBar,
    QMessageBox, QCheckBox, QComboBox
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer
from core.plugins import download_plugin_list, install_plugin
from core.editor import Editor
from core.file_manager import FileManager
from core.terminal import TerminalWidget
from core.settings import load_settings, save_settings
from core.settings_ui import SettingsUI  # import the settings UI widget
import sys
class CFL(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFL IDE")
        self.setGeometry(100, 100, 1200, 800)

        self.settings = load_settings()
        self.autosave_enabled = self.settings.get("autosave", False)

        self.init_ui()
        self.apply_theme(self.settings.get("theme", "dark"))

        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000)
        self.fullscreen = False
        self.show_startup_alert()
    def show_startup_alert(self):
        QMessageBox.information(
            self,
            "WARNING!",
            "if something goes wrong, Please read the README in GitHub."
        )


    def init_ui(self):
        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Splitter with file manager and editor
        self.splitter_top = QSplitter(Qt.Horizontal)
        self.file_manager = FileManager()
        

        self.editor = Editor()
        self.splitter_top.addWidget(self.file_manager)
        self.splitter_top.addWidget(self.editor)
        self.splitter_top.setSizes([300, 900])

        # Terminal at bottom
        self.terminal = TerminalWidget()
        
        self.terminal.setFixedHeight(200)

        # Add widgets to main layout
        self.main_layout.addWidget(self.splitter_top)
        self.main_layout.addWidget(self.terminal)

        # Connect file open request
        self.file_manager.file_open_requested.connect(self.editor.load_file)

        # Settings page (hidden by default)
        self.settings_ui = SettingsUI(self)
        self.settings_ui.hide()

        # Toolbar setup
        self.init_toolbar()

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Save button with standard Save icon
        save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        save_action = QAction(save_icon, "Save", self)
        save_action.triggered.connect(self.save_current)
        toolbar.addAction(save_action)

        # Toggle Settings button with standard Preferences icon
        settings_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self.toggle_settings_action = QAction(settings_icon, "Settings", self)
        self.toggle_settings_action.setCheckable(True)
        self.toggle_settings_action.triggered.connect(self.toggle_settings_view)
        toolbar.addAction(self.toggle_settings_action)

    def toggle_settings_view(self, checked):
        if checked:
            # Show settings UI, hide main editor layout
            self.main_layout.removeWidget(self.splitter_top)
            self.main_layout.removeWidget(self.terminal)
            self.splitter_top.hide()
            self.terminal.hide()

            self.main_layout.addWidget(self.settings_ui)
            self.settings_ui.show()
        else:
            # Hide settings UI, show main editor layout
            self.main_layout.removeWidget(self.settings_ui)
            self.settings_ui.hide()

            self.main_layout.addWidget(self.splitter_top)
            self.main_layout.addWidget(self.terminal)
            self.splitter_top.show()
            self.terminal.show()

    def save_current(self):
        if not self.editor.save_current_file():
            QMessageBox.warning(self, "Save Error", "Could not save the file.")

    def toggle_autosave(self, state):
        self.autosave_enabled = bool(state)
        self.settings["autosave"] = self.autosave_enabled
        save_settings(self.settings)

    def autosave(self):
        if self.autosave_enabled:
            self.editor.save_current_file()

    def apply_theme(self, theme_name):
        from core.settings import load_theme
        stylesheet = load_theme(theme_name)
        if stylesheet:
            self.setStyleSheet(stylesheet)
        else:
            self.setStyleSheet("")
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.fullscreen = not self.fullscreen
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CFL()
    window.show()
    sys.exit(app.exec())
